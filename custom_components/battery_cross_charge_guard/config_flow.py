"""Config flow for Battery Cross Charge Guard."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_BATTERY_A_CURRENT_LIMIT,
    CONF_BATTERY_A_HOUSE_LOAD,
    CONF_BATTERY_A_NAME,
    CONF_BATTERY_A_POWER,
    CONF_BATTERY_A_SOC,
    CONF_BATTERY_B_CURRENT_LIMIT,
    CONF_BATTERY_B_HOUSE_LOAD,
    CONF_BATTERY_B_NAME,
    CONF_BATTERY_B_POWER,
    CONF_BATTERY_B_SOC,
    CONF_CREATE_DASHBOARD,
    CONF_DASHBOARD_TITLE,
    CONF_DASHBOARD_URL_PATH,
    DEFAULT_CREATE_DASHBOARD,
    DEFAULT_DASHBOARD_TITLE,
    DEFAULT_DASHBOARD_URL_PATH,
    DOMAIN,
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_DASHBOARD_TITLE, DEFAULT_DASHBOARD_TITLE),
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_CREATE_DASHBOARD, default=DEFAULT_CREATE_DASHBOARD): bool,
                vol.Required(CONF_DASHBOARD_TITLE, default=DEFAULT_DASHBOARD_TITLE): str,
                vol.Required(CONF_DASHBOARD_URL_PATH, default=DEFAULT_DASHBOARD_URL_PATH): str,
                vol.Required(CONF_BATTERY_A_NAME): str,
                vol.Required(CONF_BATTERY_A_SOC): str,
                vol.Required(CONF_BATTERY_A_POWER): str,
                vol.Required(CONF_BATTERY_A_CURRENT_LIMIT): str,
                vol.Required(CONF_BATTERY_A_HOUSE_LOAD): str,
                vol.Required(CONF_BATTERY_B_NAME): str,
                vol.Required(CONF_BATTERY_B_SOC): str,
                vol.Required(CONF_BATTERY_B_POWER): str,
                vol.Required(CONF_BATTERY_B_CURRENT_LIMIT): str,
                vol.Required(CONF_BATTERY_B_HOUSE_LOAD): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
