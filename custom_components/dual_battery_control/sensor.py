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
    _attr_name = "Dual Battery Control Stop Event Count"
    _attr_icon = "mdi:history"

    def __init__(self, manager) -> None:
        self._manager = manager
        self._attr_unique_id = f"stop_event_count"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Dual Battery Control",
            manufacturer="GitHub",
        )

    @property
    def native_value(self) -> int:
        return len(self._manager.stop_log())

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        events = self._manager.stop_log()
        latest = events[0] if events else None
        recent = [
            {
                "timestamp": event.timestamp,
                "battery": event.battery,
                "reason": event.reason,
                "status": event.status,
                "amps": event.amps,
                "action": event.action,
                "new_limit": event.new_limit,
            }
            for event in events[:5]
        ]
        return {
            "latest_timestamp": getattr(latest, "timestamp", None),
            "latest_battery": getattr(latest, "battery", None),
            "latest_reason": getattr(latest, "reason", None),
            "latest_status": getattr(latest, "status", None),
            "latest_amps": getattr(latest, "amps", None),
            "latest_action": getattr(latest, "action", None),
            "latest_new_limit": getattr(latest, "new_limit", None),
            "recent_events": recent,
        }

    def refresh(self) -> None:
        self.async_write_ha_state()


class StopEventSummarySensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Dual Battery Control Last Stop"
    _attr_icon = "mdi:history"

    def __init__(self, manager) -> None:
        self._manager = manager
        self._attr_unique_id = f"last_stop_summary"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Dual Battery Control",
            manufacturer="GitHub",
        )

    @property
    def native_value(self) -> str:
        events = self._manager.stop_log()
        latest = events[0] if events else None
        if latest is None:
            return "No stop events yet"
        parts = [f"{latest.timestamp} — {latest.battery} ({latest.status}): {latest.reason}"]
        if latest.amps is not None:
            parts.append(f"{latest.amps}A {latest.action} → {latest.new_limit}A")
        return " | ".join(parts)

    def refresh(self) -> None:
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    manager = hass.data[DOMAIN]["manager"]
    stop_count_sensor = StopEventSensor(manager)
    stop_summary_sensor = StopEventSummarySensor(manager)
    hass.data.setdefault(DOMAIN, {}).setdefault("stop_event_sensors", []).extend(
        [stop_count_sensor, stop_summary_sensor]
    )
    async_add_entities([stop_count_sensor, stop_summary_sensor])
