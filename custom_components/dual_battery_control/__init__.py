"""Dual Battery Control integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.event import async_track_time_interval

from .const import (
    CONF_CORRECTION_ENABLED,
    DEFAULT_CORRECTION_ENABLED,
    DEFAULT_LOOP_DURATION,
    DOMAIN,
    SERVICE_PREVENT_CROSS_CHARGE,
    SERVICE_SET_AUTO_CORRECTION,
)
from .corrector import CorrectionEngine, read_battery_state
from .dashboard import build_dashboard_config, dashboard_enabled, dashboard_title, dashboard_url_path
from .manager import BatteryManager
from .models import BatteryState

_LOGGER = logging.getLogger(__name__)


async def _periodic_update(hass, entry, manager, corrector):
    """Periodic: read battery states, run detection, apply corrections."""
    for suffix in ("a", "b"):
        raw = await read_battery_state(hass, entry.data, suffix)
        if raw is None:
            continue
        battery = BatteryState(
            id=f"battery_{suffix}",
            name=raw["name"],
            soc=raw["soc"],
            voltage=0.0,
            current=0.0,
            power=raw["power"],
            charging=raw["charging"],
            discharging=raw["discharging"],
            temperature=0.0,
            online=True,
        )
        manager.update_battery(battery)

    result = manager.detect()

    for event in result.events:
        manager.record_stop_event(event.source, event.reason, event.severity.value)

    correction_enabled = entry.data.get(CONF_CORRECTION_ENABLED, DEFAULT_CORRECTION_ENABLED)
    if correction_enabled:
        await corrector.evaluate_and_apply(result)


async def _async_service_prevent_cross_charge(hass, call):
    """Service handler: run detection and correction immediately."""
    manager = hass.data[DOMAIN]["manager"]
    corrector = hass.data[DOMAIN]["corrector"]
    dry_run = call.data.get("dry_run", False)

    result = manager.detect()
    for event in result.events:
        manager.record_stop_event(event.source, event.reason, event.severity.value)

    if not dry_run:
        await corrector.evaluate_and_apply(result)
    else:
        _LOGGER.info("Dry-run cross-charge prevention: %d events", len(result.events))


async def _async_service_set_auto_correction(hass, call):
    """Service handler: enable/disable auto-correction."""
    manager = hass.data[DOMAIN]["manager"]
    enabled = call.data.get("enabled", False)
    if manager.entry_data is not None:
        manager.entry_data[CONF_CORRECTION_ENABLED] = enabled
    _LOGGER.info("Auto-correction %s", "enabled" if enabled else "disabled")


async def async_setup_entry(hass, entry) -> bool:
    manager = BatteryManager(hass=hass)
    manager.entry_data = dict(entry.data)

    corrector = CorrectionEngine(hass=hass, entry_data=manager.entry_data)
    manager.corrector = corrector

    hass.data.setdefault(DOMAIN, {})["manager"] = manager
    hass.data[DOMAIN]["corrector"] = corrector

    from homeassistant.components import frontend
    from homeassistant.components.lovelace import (
        CONF_ICON,
        CONF_REQUIRE_ADMIN,
        CONF_SHOW_IN_SIDEBAR,
        CONF_TITLE,
        CONF_URL_PATH,
        LOVELACE_DATA,
    )
    from homeassistant.components.lovelace import dashboard as lovelace_dashboard

    if dashboard_enabled(entry):
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
        else:
            hass.data[LOVELACE_DATA].dashboards[url_path] = lovelace_store
        await lovelace_store.async_save(dashboard_config)
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

    loop_interval = timedelta(seconds=DEFAULT_LOOP_DURATION)
    unsub = async_track_time_interval(
        hass,
        lambda now: _periodic_update(hass, entry, manager, corrector),
        loop_interval,
    )
    entry.async_on_unload(unsub)

    hass.services.async_register(
        DOMAIN,
        SERVICE_PREVENT_CROSS_CHARGE,
        _async_service_prevent_cross_charge,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_AUTO_CORRECTION,
        _async_service_set_auto_correction,
    )

    return True


async def async_unload_entry(hass, entry) -> bool:
    hass.data.get(DOMAIN, {}).pop("manager", None)
    hass.data.get(DOMAIN, {}).pop("corrector", None)

    hass.services.async_remove(DOMAIN, SERVICE_PREVENT_CROSS_CHARGE)
    hass.services.async_remove(DOMAIN, SERVICE_SET_AUTO_CORRECTION)

    return True
