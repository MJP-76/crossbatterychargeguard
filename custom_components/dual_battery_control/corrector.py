"""Correction engine for preventing cross-charging between batteries."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .const import (
    CONF_CORRECTION_AGGRESSIVENESS,
    CONF_CORRECTION_MODE,
    DEFAULT_CORRECTION_AGGRESSIVENESS,
    DEFAULT_CORRECTION_MODE,
)
from .models import CorrectionAction, CorrectionMode, CorrectionResult, DetectorResult

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class CorrectionEngine:
    """Reads detection results, decides corrective actions, and applies them."""

    def __init__(self, hass: HomeAssistant, entry_data: dict) -> None:
        self._hass = hass
        self._entry_data = entry_data
        self._original_values: dict[str, float] = {}
        self._battery_limit_map = self._build_limit_map()

    def _build_limit_map(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for suffix in ("a", "b"):
            name_key = f"battery_{suffix}_name"
            limit_key = f"battery_{suffix}_current_limit"
            name = self._entry_data.get(name_key, f"Battery {suffix.upper()}")
            limit_entity = self._entry_data.get(limit_key)
            if limit_entity:
                mapping[name] = limit_entity
        return mapping

    async def _read_entity_state(self, entity_id: str) -> float | None:
        state = self._hass.states.get(entity_id)
        if state is None:
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None

    @property
    def _mode(self) -> CorrectionMode:
        raw = self._entry_data.get(CONF_CORRECTION_MODE, DEFAULT_CORRECTION_MODE)
        try:
            return CorrectionMode(raw)
        except ValueError:
            return CorrectionMode(DEFAULT_CORRECTION_MODE)

    @property
    def _aggressiveness(self) -> float:
        return float(
            self._entry_data.get(CONF_CORRECTION_AGGRESSIVENESS, DEFAULT_CORRECTION_AGGRESSIVENESS)
        )

    async def evaluate_and_apply(self, result: DetectorResult) -> CorrectionResult:
        actions: list[CorrectionAction] = []
        active_batteries: set[str] = set()

        for event in result.events:
            if event.reason == "charging another battery":
                dest = event.destination
                if dest in self._battery_limit_map:
                    active_batteries.add(dest)
                    limit_entity = self._battery_limit_map[dest]

                    if limit_entity not in self._original_values:
                        original = await self._read_entity_state(limit_entity)
                        if original is not None:
                            self._original_values[limit_entity] = original

                    original = self._original_values.get(limit_entity, 100)

                    if self._mode == CorrectionMode.stop:
                        new_value = 0
                    else:
                        reduction = original * self._aggressiveness
                        new_value = max(0, original - reduction)

                    actions.append(
                        CorrectionAction(
                            entity_id=limit_entity,
                            service="set_value",
                            service_data={"value": new_value},
                            reason=(
                                f"Cross-charge from {event.source}: "
                                f"set {limit_entity} to {new_value}"
                            ),
                        )
                    )

        for name, limit_entity in self._battery_limit_map.items():
            if name not in active_batteries and limit_entity in self._original_values:
                original = self._original_values.pop(limit_entity)
                actions.append(
                    CorrectionAction(
                        entity_id=limit_entity,
                        service="set_value",
                        service_data={"value": original},
                        reason=f"Cross-charge cleared for {name}: restore {limit_entity} to {original}",
                    )
                )

        for action in actions:
            try:
                await self._hass.services.async_call(
                    "number",
                    action.service,
                    {"entity_id": action.entity_id, **action.service_data},
                )
            except Exception:
                _LOGGER.warning("Correction failed for %s", action.entity_id, exc_info=True)

        return CorrectionResult(actions=actions, applied=bool(actions))


async def read_battery_state(hass: HomeAssistant, entry_data: dict, suffix: str) -> dict | None:
    """Read configured entity values for a battery and return raw state dict."""
    name_key = f"battery_{suffix}_name"
    soc_key = f"battery_{suffix}_soc"
    power_key = f"battery_{suffix}_power"

    name = entry_data.get(name_key, f"Battery {suffix.upper()}")
    soc_entity = entry_data.get(soc_key)
    power_entity = entry_data.get(power_key)

    if not soc_entity or not power_entity:
        return None

    soc_state = hass.states.get(soc_entity)
    power_state = hass.states.get(power_entity)

    if soc_state is None or power_state is None:
        return None

    try:
        soc = float(soc_state.state)
        power = float(power_state.state)
    except (ValueError, TypeError):
        return None

    return {
        "name": name,
        "soc": soc,
        "power": power,
        "charging": power < 0,
        "discharging": power > 0,
    }
