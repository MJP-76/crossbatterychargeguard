"""Balancing logic for two batteries."""

from __future__ import annotations

from dataclasses import dataclass

from .const import DEFAULT_DEADBAND, DEFAULT_MAX_CURRENT, DEFAULT_RAMP_RATE, DEFAULT_RESERVE_SOC


@dataclass(frozen=True)
class BatteryState:
    soc: float
    capacity_kwh: float


@dataclass(frozen=True)
class BalanceCommand:
    charge_a: float
    charge_b: float
    discharge_a: float
    discharge_b: float
    target_a: float
    target_b: float


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _usable_energy(state: BatteryState, reserve_soc: float) -> float:
    return max(0.0, state.capacity_kwh * max(0.0, state.soc - reserve_soc) / 100.0)


def _ramp(current: float, target: float, ramp_rate: float) -> float:
    delta = target - current
    if abs(delta) <= ramp_rate:
        return target
    return current + ramp_rate if delta > 0 else current - ramp_rate


class BatteryBalancer:
    """Calculate per-battery current targets."""

    def __init__(
        self,
        reserve_soc: float = DEFAULT_RESERVE_SOC,
        max_current: float = DEFAULT_MAX_CURRENT,
        ramp_rate: float = DEFAULT_RAMP_RATE,
        deadband: float = DEFAULT_DEADBAND,
    ) -> None:
        self.reserve_soc = reserve_soc
        self.max_current = max_current
        self.ramp_rate = ramp_rate
        self.deadband = deadband
        self._previous = BalanceCommand(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def calculate(
        self,
        battery_a: BatteryState,
        battery_b: BatteryState,
        total_current: float,
    ) -> BalanceCommand:
        reserve = self.reserve_soc
        usable_a = _usable_energy(battery_a, reserve)
        usable_b = _usable_energy(battery_b, reserve)
        total_usable = usable_a + usable_b

        if total_usable <= 0:
            share_a = share_b = 0.5
        else:
            share_a = usable_a / total_usable
            share_b = usable_b / total_usable

        if abs(battery_a.soc - battery_b.soc) <= self.deadband:
            share_a = share_b = 0.5

        if total_current >= 0:
            target_a = _clamp(total_current * share_a, 0.0, self.max_current)
            target_b = _clamp(total_current * share_b, 0.0, self.max_current)
            discharge_a, discharge_b = target_a, target_b
            charge_a = charge_b = 0.0
        else:
            target_a = _clamp(abs(total_current) * share_a, 0.0, self.max_current)
            target_b = _clamp(abs(total_current) * share_b, 0.0, self.max_current)
            charge_a, charge_b = target_a, target_b
            discharge_a = discharge_b = 0.0

        command = BalanceCommand(
            charge_a=_ramp(self._previous.charge_a, charge_a, self.ramp_rate),
            charge_b=_ramp(self._previous.charge_b, charge_b, self.ramp_rate),
            discharge_a=_ramp(self._previous.discharge_a, discharge_a, self.ramp_rate),
            discharge_b=_ramp(self._previous.discharge_b, discharge_b, self.ramp_rate),
            target_a=target_a,
            target_b=target_b,
        )
        self._previous = command
        return command
