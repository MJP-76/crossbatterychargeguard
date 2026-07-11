"""Diagnostic sensor helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiagnosticSnapshot:
    usable_energy_a: float
    usable_energy_b: float
    share_a: float
    share_b: float
    target_a: float
    target_b: float

