"""Config flow for Nødvarsel."""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback

from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    RSS_URL,
)


class NodvarselConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Nødvarsel-integrasjonen."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Håndter brukerens oppsettsteg."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Valider tilkobling til RSS-feeden
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        RSS_URL,
                        timeout=aiohttp.ClientTimeout(total=10),
                        headers={
                            "User-Agent": "Nodvarsel-HA-Integration/1.0.0"
                        },
                    ) as response:
                        if response.status != 200:
                            errors["base"] = "cannot_connect"
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Uventet feil under oppsett")
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(
                    title="Nødvarsel",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry,
    ) -> NodvarselOptionsFlow:
        """Returner options flow."""
        return NodvarselOptionsFlow()


class NodvarselOptionsFlow(OptionsFlow):
    """Options flow for å endre innstillinger etter installasjon."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Håndter options-steget."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(
                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
            ),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=current_interval,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                }
            ),
        )
