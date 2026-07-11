"""Battery discovery and detection manager."""

from __future__ import annotations

from dataclasses import dataclass, field

from .diagnostics import DiagnosticsSnapshot, build_diagnostics
from .detector import CrossChargeDetector
from .models import AnalysisReport, BatteryState, DetectorResult
from .repair import build_repair_issue, repair_issue_payload
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

    def analyze(self) -> AnalysisReport:
        result = self.detect()
        snapshot = build_diagnostics(result)
        issue = build_repair_issue(snapshot)
        return AnalysisReport(
            result=result,
            diagnostics={
                "battery_count": snapshot.battery_count,
                "cross_charge_events": snapshot.cross_charge_events,
                "largest_transfer": snapshot.largest_transfer,
                "imbalance": snapshot.imbalance,
                "critical": snapshot.critical,
            },
            repair_issue=repair_issue_payload(issue),
        )
