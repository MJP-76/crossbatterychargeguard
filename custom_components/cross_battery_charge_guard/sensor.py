"""Sensor platform for stop-event history."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


class StopEventSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Stop Event Count"
    _attr_icon = "mdi:history"

    def __init__(self, manager) -> None:
        self._manager = manager
        self._attr_unique_id = f"{DOMAIN}_stop_event_count"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Cross Battery Charge Guard",
            manufacturer="GitHub",
        )

    @property
    def native_value(self) -> int:
        return len(self._manager.stop_log())

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        events = self._manager.stop_log()
        latest = events[0] if events else None
        return {
            "latest_timestamp": getattr(latest, "timestamp", None),
            "latest_battery": getattr(latest, "battery", None),
            "latest_reason": getattr(latest, "reason", None),
            "latest_status": getattr(latest, "status", None),
        }

    def refresh(self) -> None:
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    manager = hass.data[DOMAIN]["manager"]
    sensor = StopEventSensor(manager)
    hass.data.setdefault(DOMAIN, {}).setdefault("stop_event_sensors", []).append(sensor)
    async_add_entities([sensor])
