"""Battery discovery and detection manager."""

from __future__ import annotations

from dataclasses import dataclass, field

from .diagnostics import DiagnosticsSnapshot, build_diagnostics
from .detector import CrossChargeDetector
from .models import BatteryState, DetectorResult
from .repair import RepairIssue, build_repair_issue
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

    def analyze(self) -> tuple[DetectorResult, DiagnosticsSnapshot, RepairIssue | None]:
        result = self.detect()
        snapshot = build_diagnostics(result)
        issue = build_repair_issue(snapshot)
        return result, snapshot, issue
