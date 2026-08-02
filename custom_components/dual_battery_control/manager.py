"""Battery discovery, detection, and correction manager."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .diagnostics import DiagnosticsSnapshot, build_diagnostics
from .detector import CrossChargeDetector
from .models import AnalysisReport, BatteryState, CorrectionResult, DetectorResult, StopEvent
from .repair import build_repair_issue, repair_issue_payload
from .registry import BatteryRegistry

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from .corrector import CorrectionEngine


@dataclass(slots=True)
class BatteryManager:
    """Keep the registry, detector, and correction engine in sync."""

    registry: BatteryRegistry = field(default_factory=BatteryRegistry)
    detector: CrossChargeDetector = field(default_factory=CrossChargeDetector)
    stop_events: deque[StopEvent] = field(default_factory=lambda: deque(maxlen=10))
    hass: HomeAssistant | None = None
    corrector: CorrectionEngine | None = None
    entry_data: dict | None = None

    def update_battery(self, battery: BatteryState) -> None:
        self.registry.upsert(battery)
        self.detector.registry = self.registry

    def detect(self) -> DetectorResult:
        self.detector.registry = self.registry
        return self.detector.detect()

    async def async_correct(self, result: DetectorResult | None = None) -> CorrectionResult:
        if self.corrector is None:
            return CorrectionResult(actions=[], applied=False)
        if result is None:
            result = self.detect()
        return await self.corrector.evaluate_and_apply(result)

    def analyze(self) -> AnalysisReport:
        result = self.detect()
        snapshot = build_diagnostics(result)
        issue = build_repair_issue(snapshot)
        if result.events:
            for event in result.events:
                self.record_stop_event(event.source, event.reason, event.severity.value)
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

    def record_stop_event(
        self,
        battery: str,
        reason: str,
        status: str,
        amps: float | None = None,
        action: str | None = None,
        new_limit: float | None = None,
    ) -> None:
        self.stop_events.appendleft(
            StopEvent(
                timestamp=datetime.now(timezone.utc).isoformat(),
                battery=battery,
                reason=reason,
                status=status,
                amps=amps,
                action=action,
                new_limit=new_limit,
            )
        )
        if self.hass is not None:
            for sensor in self.hass.data.get("dual_battery_control", {}).get("stop_event_sensors", []):
                sensor.refresh()

    def stop_log(self) -> list[StopEvent]:
        return list(self.stop_events)
