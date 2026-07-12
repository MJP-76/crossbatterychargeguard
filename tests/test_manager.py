import unittest

from custom_components.cross_battery_charge_guard.manager import BatteryManager
from custom_components.cross_battery_charge_guard.models import BatteryState


class ManagerTests(unittest.TestCase):
    def test_registry_updates_and_detects(self):
        manager = BatteryManager()
        manager.update_battery(BatteryState("a", "Battery A", 95, 50, 0, 100, False, False, 25, True))
        manager.update_battery(BatteryState("b", "Battery B", 41, 50, 0, -100, False, True, 25, True))

        result = manager.detect()

        self.assertEqual(result.battery_count, 2)
        self.assertTrue(result.events)

    def test_analyze_returns_diagnostics_and_issue(self):
        manager = BatteryManager()
        manager.update_battery(BatteryState("a", "Battery A", 95, 50, 0, 100, False, False, 55, True))

        report = manager.analyze()

        self.assertEqual(report.result.battery_count, 1)
        self.assertTrue(report.diagnostics["critical"])
        self.assertIsNotNone(report.repair_issue)

    def test_record_stop_event_tracks_history(self):
        manager = BatteryManager()
        manager.record_stop_event("battery-a", "cross-charge", "warning")

        log = manager.stop_log()

        self.assertEqual(len(log), 1)
        self.assertEqual(log[0].battery, "battery-a")
        self.assertEqual(log[0].reason, "cross-charge")
        self.assertEqual(log[0].status, "warning")


if __name__ == "__main__":
    unittest.main()
