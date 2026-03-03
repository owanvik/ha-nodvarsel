"""Diagnostics for Nødvarsel."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import NodvarselCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Returner diagnostikkdata for en config entry."""
    coordinator: NodvarselCoordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "config": dict(entry.data),
        "options": dict(entry.options),
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_update_success_time": str(coordinator.last_update_success_time),
            "update_interval": str(coordinator.update_interval),
            "consecutive_errors": coordinator.consecutive_errors,
            "data": coordinator.data,
        },
    }
