from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([CheckIntervalNumber(entry)])


class CheckIntervalNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Check Interval"
    _attr_native_min_value = 30
    _attr_native_max_value = 3600
    _attr_native_step = 10
    _attr_native_unit_of_measurement = "s"
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:timer-outline"

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_check_interval"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Dual Battery Control",
            manufacturer="GitHub",
        )

    @property
    def native_value(self) -> float:
        return float(
            self._entry.options.get(
            CONF_CHECK_INTERVAL,
            self._entry.data.get(CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL),
            )
        )

    async def async_set_native_value(self, value: float) -> None:
        new_options = {**self._entry.options, CONF_CHECK_INTERVAL: int(value)}
        await self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        await self.async_write_ha_state()
