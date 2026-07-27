# Cross Battery Charge Guard

Home Assistant custom component for guarding against cross-charging between batteries.

Repository: `MJP-76/crossbatterychargeguard`

HACS-compatible metadata is included at the repository root in `hacs.json`.
The integration can create a Lovelace dashboard automatically from the entities you choose during setup, with separate battery blocks and live SOC/power trend cards.
It is configured through Home Assistant's UI config flow, not `configuration.yaml`.
Current release: `0.1.29`.
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

## Support me

If you find this project useful, and would like to help support its continued development, you can do so here:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=000000)](https://www.buymeacoffee.com/mjp76)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=ffffff)](https://ko-fi.com/mjp76)
[![Octopus Energy — you get £50, I get £50](https://img.shields.io/badge/Octopus%20Energy-%E2%80%94%20you%20get%20%C2%A350%2C%20I%20get%20%C2%A350-14294A?style=for-the-badge&logo=octopus-energy&logoColor=ffffff)](https://share.octopus.energy/iron-moose-196)