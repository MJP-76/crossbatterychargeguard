# Cross Battery Charge Guard

Home Assistant custom component for guarding against cross-charging between batteries.

Repository: `MJP-76/crossbatterychargeguard`

HACS-compatible metadata is included at the repository root in `hacs.json`.
The integration can create a Lovelace dashboard automatically from the entities you choose during setup, with separate battery blocks and live SOC/power trend cards.
It is configured through Home Assistant's UI config flow, not `configuration.yaml`.
Current release: `0.1.18`.
Default dashboard URL path: `crossbatterychargeguard`.

## Included

- `custom_components/cross_battery_charge_guard/`
- battery registry
- rule engine
- diagnostics
- repairs helper
- manifest and packaging metadata
- tests
- config flow and options flow for selecting battery entities and dashboard settings

## Deferred

- Battery load balancing has been moved to a later todo and is not included in this version.