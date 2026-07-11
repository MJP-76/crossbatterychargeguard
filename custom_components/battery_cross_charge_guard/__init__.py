"""Battery Cross Charge Guard integration."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace import (
    CONF_ICON,
    CONF_REQUIRE_ADMIN,
    CONF_SHOW_IN_SIDEBAR,
    CONF_TITLE,
    CONF_URL_PATH,
    LOVELACE_DATA,
)
from homeassistant.components.lovelace import dashboard as lovelace_dashboard
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import CONF_CREATE_DASHBOARD, DEFAULT_CREATE_DASHBOARD, DOMAIN, PLATFORMS
from .dashboard import build_dashboard_config, dashboard_enabled, dashboard_title, dashboard_url_path

_LOGGER = logging.getLogger(__name__)
_FRONTEND_URL = "/battery_cross_charge_guard/dashboard.js"
_FRONTEND_FILE = Path(__file__).parent / "frontend" / "dashboard.js"
_FRONTEND_REGISTERED = "battery_cross_charge_guard_frontend_registered"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await _async_register_frontend(hass)
    await _async_ensure_dashboard(hass, entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_register_frontend(hass: HomeAssistant) -> None:
    if hass.data.get(_FRONTEND_REGISTERED):
        return
    hass.http.register_static_paths([StaticPathConfig("/battery_cross_charge_guard", str(_FRONTEND_FILE.parent), cache_headers=False)])
    add_extra_js_url(hass, _FRONTEND_URL)
    hass.data[_FRONTEND_REGISTERED] = True


async def _async_ensure_dashboard(hass: HomeAssistant, entry: ConfigEntry) -> None:
    if not dashboard_enabled(entry):
        return
    title = dashboard_title(entry)
    url_path = dashboard_url_path(entry)
    item = {
        CONF_TITLE: title,
        CONF_URL_PATH: url_path,
        CONF_ICON: "mdi:battery",
        CONF_SHOW_IN_SIDEBAR: True,
        CONF_REQUIRE_ADMIN: False,
    }
    lovelace_store = hass.data[LOVELACE_DATA].dashboards.get(url_path)
    if lovelace_store is None:
        lovelace_store = lovelace_dashboard.LovelaceStorage(hass, item)
        hass.data[LOVELACE_DATA].dashboards[url_path] = lovelace_store
    await lovelace_store.async_save(build_dashboard_config(hass, entry))
    hass.bus.async_fire("lovelace_updated", {"url_path": url_path, "updated": True})
    frontend.async_register_built_in_panel(
        hass,
        "lovelace",
        frontend_url_path=url_path,
        require_admin=False,
        show_in_sidebar=True,
        sidebar_title=title,
        sidebar_icon="mdi:battery",
        config={"mode": "storage"},
        update=True,
    )
