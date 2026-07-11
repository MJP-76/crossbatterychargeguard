"""Compatibility wrapper for the renamed SolaX cross battery guard config flow."""

from custom_components.solax_cross_battery_guard.config_flow import (  # noqa: F401
    ConfigFlow,
    OptionsFlowHandler,
    async_get_options_flow,
)
