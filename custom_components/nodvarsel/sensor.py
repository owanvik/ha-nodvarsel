"""Sensor-plattform for Nødvarsel."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
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
    """Sett opp sensorer fra config entry."""
    coordinator: NodvarselCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        NodvarselCountSensor(coordinator, entry),
        NodvarselLastAlertSensor(coordinator, entry),
        NodvarselLastUpdateSensor(coordinator, entry),
    ])


class NodvarselSensorBase(CoordinatorEntity[NodvarselCoordinator], SensorEntity):
    """Baseklasse for Nødvarsel-sensorer."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: NodvarselCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialiser sensor."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Nødvarsel",
            manufacturer="DSB, Politiet og Sivilforsvaret",
            model="Nødvarsel RSS",
            configuration_url="https://www.nodvarsel.no",
            entry_type=DeviceEntryType.SERVICE,
        )
        self._entry = entry


class NodvarselCountSensor(NodvarselSensorBase):
    """Sensor som viser antall aktive nødvarsler."""

    _attr_translation_key = "alert_count"
    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "varsler"

    def __init__(
        self,
        coordinator: NodvarselCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialiser sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_count"

    @property
    def native_value(self) -> int | None:
        """Returner antall aktive varsler."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data["alert_count"]


class NodvarselLastAlertSensor(NodvarselSensorBase):
    """Sensor som viser tittel og detaljer for siste nødvarsel."""

    _attr_translation_key = "last_alert"
    _attr_icon = "mdi:alert-circle-outline"

    def __init__(
        self,
        coordinator: NodvarselCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialiser sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_last_alert"

    @property
    def native_value(self) -> str | None:
        """Returner tittel på siste varsel."""
        if self.coordinator.data is None:
            return None
        last_alert = self.coordinator.data.get("last_alert")
        if last_alert:
            return last_alert["title"][:255]
        return "Ingen aktive varsler"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Returner detaljer om siste varsel."""
        if self.coordinator.data is None:
            return {}
        last_alert = self.coordinator.data.get("last_alert")
        if last_alert:
            return {
                "title": last_alert["title"],
                "description": last_alert["description"],
                "link": last_alert["link"],
                "updated": last_alert["updated"],
                "source": "https://www.nodvarsel.no",
            }
        return {
            "source": "https://www.nodvarsel.no",
        }


class NodvarselLastUpdateSensor(NodvarselSensorBase):
    """Sensor som viser tidspunkt for siste vellykkede oppdatering."""

    _attr_translation_key = "last_update"
    _attr_icon = "mdi:clock-check-outline"
    _attr_device_class = "timestamp"

    def __init__(
        self,
        coordinator: NodvarselCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialiser sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_last_update"

    @property
    def native_value(self) -> datetime | None:
        """Returner tidspunkt for siste vellykkede poll."""
        if self.coordinator.last_update_success_time is not None:
            return self.coordinator.last_update_success_time
        return datetime.now(timezone.utc)
