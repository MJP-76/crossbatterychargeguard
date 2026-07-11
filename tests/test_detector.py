import unittest

from custom_components.battery_cross_charge_guard.detector import CrossChargeDetector
from custom_components.battery_cross_charge_guard.diagnostics import build_diagnostics, diagnostics_payload
from custom_components.battery_cross_charge_guard.models import BatteryState
from custom_components.battery_cross_charge_guard.repair import build_repair_issue


class DetectorTests(unittest.TestCase):
    def test_detects_soc_difference(self):
        detector = CrossChargeDetector()
        detector.upsert(BatteryState("a", "Battery A", 95, 50, 0, 100, False, False, 25, True))
        detector.upsert(BatteryState("b", "Battery B", 41, 50, 0, -100, False, True, 25, True))

        result = detector.detect()

        self.assertEqual(result.battery_count, 2)
        self.assertGreaterEqual(result.max_soc_difference, 54)
        self.assertTrue(result.events)

    def test_diagnostics_and_repair(self):
        detector = CrossChargeDetector()
        detector.upsert(BatteryState("a", "Battery A", 95, 50, 0, 100, False, False, 55, True))

        result = detector.detect()
        snapshot = build_diagnostics(result)
        payload = diagnostics_payload(snapshot)
        issue = build_repair_issue(snapshot)

        self.assertEqual(payload["battery_count"], 1)
        self.assertTrue(payload["critical"])
        self.assertIsNotNone(issue)


if __name__ == "__main__":
    unittest.main()
