"""DataUpdateCoordinator for Nødvarsel."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import ATOM_NS, DOMAIN, LOGGER, RSS_URL


class NodvarselCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator som henter nødvarsler fra nodvarsel.no RSS-feed."""

    def __init__(
        self,
        hass: HomeAssistant,
        scan_interval: timedelta,
    ) -> None:
        """Initialiser coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Hent data fra RSS-feed."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    RSS_URL,
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={
                        "User-Agent": "Nodvarsel-HA-Integration/1.0.0"
                    },
                ) as response:
                    if response.status != 200:
                        raise UpdateFailed(
                            f"Feil ved henting av RSS-feed: HTTP {response.status}"
                        )
                    xml_text = await response.text()

        except aiohttp.ClientError as err:
            raise UpdateFailed(
                f"Nettverksfeil ved henting av nødvarsler: {err}"
            ) from err
        except TimeoutError as err:
            raise UpdateFailed(
                "Tidsavbrudd ved henting av nødvarsler"
            ) from err

        return self._parse_rss(xml_text)

    def _parse_rss(self, xml_text: str) -> dict[str, Any]:
        """Pars RSS XML og returner strukturert data."""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as err:
            raise UpdateFailed(
                f"Kunne ikke tolke RSS-feed: {err}"
            ) from err

        channel = root.find("channel")
        if channel is None:
            raise UpdateFailed("RSS-feed mangler <channel>-element")

        alerts: list[dict[str, str]] = []
        for item in channel.findall("item"):
            alert = {
                "guid": self._xml_text(item, "guid"),
                "link": self._xml_text(item, "link"),
                "title": self._xml_text(item, "title"),
                "description": self._xml_text(item, "description"),
                "updated": self._xml_text(
                    item, f"{{{ATOM_NS}}}updated"
                ) or self._xml_text(item, "updated"),
            }
            alerts.append(alert)

        has_active = len(alerts) > 0
        last_alert = alerts[0] if has_active else None

        return {
            "alerts": alerts,
            "alert_count": len(alerts),
            "has_active_alert": has_active,
            "last_alert": last_alert,
        }

    @staticmethod
    def _xml_text(parent: ET.Element, tag: str) -> str:
        """Hent tekst fra et XML-barn-element."""
        el = parent.find(tag)
        if el is not None and el.text:
            return el.text.strip()
        return ""
