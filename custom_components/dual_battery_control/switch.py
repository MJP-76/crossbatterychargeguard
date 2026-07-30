from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CORRECTION_ENABLED, DEFAULT_CORRECTION_ENABLED, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([AutoCorrectionSwitch(entry)])


class AutoCorrectionSwitch(SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Auto Correction"

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_auto_correction"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Dual Battery Control",
            manufacturer="GitHub",
        )

    @property
    def is_on(self) -> bool:
        return self._entry.options.get(
            CONF_CORRECTION_ENABLED,
            self._entry.data.get(CONF_CORRECTION_ENABLED, DEFAULT_CORRECTION_ENABLED),
        )

    async def async_turn_on(self, **kwargs) -> None:
        await self._set_option(CONF_CORRECTION_ENABLED, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._set_option(CONF_CORRECTION_ENABLED, False)

    async def _set_option(self, key: str, value: object) -> None:
        new_options = {**self._entry.options, key: value}
        await self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        await self.async_write_ha_state()
