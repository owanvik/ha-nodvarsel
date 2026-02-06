"""Binary sensor-plattform for Nødvarsel."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import NodvarselCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sett opp binary sensor fra config entry."""
    coordinator: NodvarselCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NodvarselBinarySensor(coordinator, entry)])


class NodvarselBinarySensor(CoordinatorEntity[NodvarselCoordinator], BinarySensorEntity):
    """Binary sensor som viser om det finnes aktive nødvarsler."""

    _attr_has_entity_name = True
    _attr_translation_key = "active_alert"
    _attr_device_class = BinarySensorDeviceClass.SAFETY
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: NodvarselCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialiser binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_active"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Nødvarsel",
            manufacturer="DSB, Politiet og Sivilforsvaret",
            model="Nødvarsel RSS",
            configuration_url="https://www.nodvarsel.no",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def icon(self) -> str:
        """Returner ikon basert på tilstand."""
        if self.is_on:
            return "mdi:alert-octagram"
        return "mdi:shield-check"

    @property
    def is_on(self) -> bool | None:
        """Returner True hvis det finnes aktive varsler."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data["has_active_alert"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Returner ekstra attributter med varseldetaljer."""
        if self.coordinator.data is None:
            return {}
        return {
            "alerts": self.coordinator.data["alerts"],
            "alert_count": self.coordinator.data["alert_count"],
            "source": "https://www.nodvarsel.no",
        }
