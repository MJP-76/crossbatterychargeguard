"""Battery discovery and detection manager."""

from __future__ import annotations

from dataclasses import dataclass, field

from .detector import CrossChargeDetector
from .models import BatteryState, DetectorResult
from .registry import BatteryRegistry


@dataclass(slots=True)
class BatteryManager:
    """Keep the registry and detector in sync."""

    registry: BatteryRegistry = field(default_factory=BatteryRegistry)
    detector: CrossChargeDetector = field(default_factory=CrossChargeDetector)

    def update_battery(self, battery: BatteryState) -> None:
        self.registry.upsert(battery)
        self.detector.registry = self.registry

    def detect(self) -> DetectorResult:
        self.detector.registry = self.registry
        return self.detector.detect()

