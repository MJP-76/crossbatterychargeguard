from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CORRECTION_MODE, DEFAULT_CORRECTION_MODE, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([CorrectionModeSelect(entry)])


class CorrectionModeSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Correction Mode"
    _attr_options = ["off", "stop", "reduce"]
    _attr_icon = "mdi:tune-variant"

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_correction_mode"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Dual Battery Control",
            manufacturer="GitHub",
        )

    @property
    def current_option(self) -> str | None:
        return str(
            self._entry.options.get(
            CONF_CORRECTION_MODE,
            self._entry.data.get(CONF_CORRECTION_MODE, DEFAULT_CORRECTION_MODE),
            )
        )

    async def async_select_option(self, option: str) -> None:
        new_options = {**self._entry.options, CONF_CORRECTION_MODE: option}
        await self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        await self.async_write_ha_state()
