"""Constants for Battery Cross Charge Guard."""

DOMAIN = "battery_cross_charge_guard"
PLATFORMS: list[str] = ["sensor", "binary_sensor"]
DEFAULT_RESERVE_SOC = 10.0
DEFAULT_DEADBAND = 0.2
DEFAULT_MAX_CROSS_CHARGE_WATTS = 100.0
DEFAULT_MAX_SOC_DIFFERENCE = 30.0
DEFAULT_LOOP_DURATION = 300
DEFAULT_MAX_BATTERY_TEMP = 50.0
