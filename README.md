# ha-solax-cross-battery-guard

Home Assistant custom component for guarding against cross-charging between batteries.

HACS-compatible metadata is included at the repository root in `hacs.json`.
The integration can create a Lovelace dashboard automatically from the entities you choose during setup, with graphical SOC gauges, battery cards, and live trend graphs.
The repo also includes a ready-to-import Lovelace dashboard template in `lovelace-dashboard.yaml`.

## Included

- `custom_components/battery_cross_charge_guard/`
- battery registry
- rule engine
- diagnostics
- repairs helper
- manifest and packaging metadata
- tests
- `lovelace-dashboard.yaml` sample dashboard view for Home Assistant import
- config flow for selecting battery entities and dashboard settings

## Deferred

- Battery load balancing has been moved to a later todo and is not included in this version.