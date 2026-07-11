"""Battery Cross Charge Guard integration."""

from __future__ import annotations

import logging

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

from .const import DOMAIN
from .dashboard import build_dashboard_config, dashboard_enabled, dashboard_title, dashboard_url_path

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await _async_ensure_dashboard(hass, entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True

async def _async_ensure_dashboard(hass: HomeAssistant, entry: ConfigEntry) -> None:
    if not dashboard_enabled(entry):
        return
    title = dashboard_title(entry)
    url_path = dashboard_url_path(entry)
    item = {
        "id": url_path,
        CONF_TITLE: title,
        CONF_URL_PATH: url_path,
        CONF_ICON: "mdi:battery",
        CONF_SHOW_IN_SIDEBAR: True,
        CONF_REQUIRE_ADMIN: False,
    }
    dashboard_config = build_dashboard_config(hass, entry)
    dashboard_config["id"] = url_path
    lovelace_store = hass.data[LOVELACE_DATA].dashboards.get(url_path)
    if lovelace_store is None:
        lovelace_store = lovelace_dashboard.LovelaceStorage(hass, item)
        hass.data[LOVELACE_DATA].dashboards[url_path] = lovelace_store
    await lovelace_store.async_save(dashboard_config)
    hass.bus.async_fire("lovelace_updated", {"url_path": url_path, "updated": True})
    from homeassistant.components import frontend

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
