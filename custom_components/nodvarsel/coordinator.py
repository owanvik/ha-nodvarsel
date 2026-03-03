"""DataUpdateCoordinator for Nødvarsel."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import ATOM_NS, DOMAIN, EVENT_NEW_ALERT, LOGGER, MAX_BACKOFF_INTERVAL, RSS_URL


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
        self._base_scan_interval = scan_interval
        self._known_guids: set[str] = set()
        self._initialized = False
        self.consecutive_errors = 0

    async def _async_update_data(self) -> dict[str, Any]:
        """Hent data fra RSS-feed med eksponentiell backoff ved feil."""
        try:
            data = await self._fetch_and_parse()
        except UpdateFailed:
            self.consecutive_errors += 1
            backoff_seconds = min(
                self._base_scan_interval.total_seconds()
                * (2 ** (self.consecutive_errors - 1)),
                MAX_BACKOFF_INTERVAL,
            )
            self.update_interval = timedelta(seconds=backoff_seconds)
            LOGGER.warning(
                "Oppdatering feilet (forsøk %d), neste forsøk om %.0f sekunder",
                self.consecutive_errors,
                backoff_seconds,
            )
            raise

        self.consecutive_errors = 0
        self.update_interval = self._base_scan_interval
        self._fire_new_alert_events(data)
        return data

    async def _fetch_and_parse(self) -> dict[str, Any]:
        """Hent og pars RSS-feed."""
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

    def _fire_new_alert_events(self, data: dict[str, Any]) -> None:
        """Fire event for hvert nytt varsel som ikke er sett før."""
        new_guids = {a["guid"] for a in data["alerts"] if a["guid"]}
        if self._initialized:
            for alert in data["alerts"]:
                if alert["guid"] and alert["guid"] not in self._known_guids:
                    self.hass.bus.async_fire(
                        EVENT_NEW_ALERT,
                        {"alert": alert},
                    )
                    LOGGER.debug("Nytt nødvarsel: %s", alert.get("title"))
        self._known_guids = new_guids
        self._initialized = True

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
