# Dual Battery Control

[![Home Assistant][badge-home-assistant]][home-assistant]
[![HACS][badge-hacs]][hacs]
[![HACS Validation][badge-hacs-validation]][workflow-hacs-validation]
[![Hassfest][badge-hassfest]][workflow-hassfest]
[![CI][badge-ci]][workflow-ci]
[![Release][badge-release]][releases]
![Status][badge-status]

Home Assistant custom component for monitoring and preventing cross-charging between batteries in dual-inverter setups.

Repository: `MJP-76/ha-dual-battery-control`

HACS-compatible metadata is included at the repository root in `hacs.json`.
The integration can create a Lovelace dashboard automatically from the entities you choose during setup, with separate battery blocks and live SOC/power trend cards.
It is configured through Home Assistant's UI config flow, not `configuration.yaml`.
Current release: `0.2.0`.
Default dashboard URL path: `dualbatterycontrol`.

## Background

This component was created to solve cross-charging between two batteries connected to a pair of **SolaX SKU-5000E inverters** that do not support Master/Slave co-ordination. In such setups each inverter independently decides when to charge or discharge its battery, which can lead to one battery discharging into the other — wasting energy and reducing efficiency. Dual Battery Control detects this condition and can automatically adjust charge current limits to break the loop.

## Included

- `custom_components/dual_battery_control/`
- battery registry
- rule engine (cross-charge, SOC divergence, thermal)
- correction engine — automatic prevention of cross-charging
- diagnostics
- repairs helper
- manifest and packaging metadata
- tests
- config flow and options flow for selecting battery entities, dashboard, and correction settings
- two services: `prevent_cross_charge` (manual trigger with dry-run mode) and `set_auto_correction` (toggle)

## Support me

If you find this project useful, and would like to help support its continued development, you can do so here:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=000000)](https://www.buymeacoffee.com/mjp76)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=ffffff)](https://ko-fi.com/mjp76)
[![Octopus Energy — you get £50, I get £50](https://img.shields.io/badge/Octopus%20Energy-%E2%80%94%20you%20get%20%C2%A350%2C%20I%20get%20%C2%A350-14294A?style=for-the-badge&logo=octopus-energy&logoColor=ffffff)](https://share.octopus.energy/iron-moose-196)

[badge-home-assistant]: https://img.shields.io/badge/Home%20Assistant-41BDF5?style=flat-square&logo=homeassistant&logoColor=white
[home-assistant]: https://www.home-assistant.io/
[badge-hacs]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg
[hacs]: https://github.com/hacs/integration
[badge-hacs-validation]: https://img.shields.io/badge/HACS%20Validation-passing-brightgreen
[workflow-hacs-validation]: https://github.com/MJP-76/ha-dual-battery-control/actions/workflows/validate.yml
[badge-hassfest]: https://img.shields.io/github/actions/workflow/status/MJP-76/ha-dual-battery-control/hassfest.yml?branch=main&label=Hassfest
[workflow-hassfest]: https://github.com/MJP-76/ha-dual-battery-control/actions/workflows/hassfest.yml
[badge-ci]: https://github.com/MJP-76/ha-dual-battery-control/actions/workflows/ci.yml/badge.svg
[workflow-ci]: https://github.com/MJP-76/ha-dual-battery-control/actions/workflows/ci.yml
[badge-release]: https://img.shields.io/github/v/release/MJP-76/ha-dual-battery-control?style=flat&label=Release
[releases]: https://github.com/MJP-76/ha-dual-battery-control/releases
[badge-status]: https://img.shields.io/badge/Status-experimental-yellow
