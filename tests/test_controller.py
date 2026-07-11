import unittest

from custom_components.battery_cross_charge_guard.controller import BatteryBalancer, BatteryState


class BatteryBalancerTests(unittest.TestCase):
    def test_weights_by_usable_energy(self):
        balancer = BatteryBalancer(ramp_rate=100)
        cmd = balancer.calculate(
            BatteryState(soc=42, capacity_kwh=15),
            BatteryState(soc=55, capacity_kwh=8),
            40,
        )
        self.assertAlmostEqual(cmd.target_a, 22.8571428571, places=6)
        self.assertAlmostEqual(cmd.target_b, 17.1428571429, places=6)

    def test_uses_equal_share_within_deadband(self):
        balancer = BatteryBalancer(ramp_rate=100, deadband=1.0)
        cmd = balancer.calculate(
            BatteryState(soc=40.1, capacity_kwh=10),
            BatteryState(soc=40.5, capacity_kwh=20),
            30,
        )
        self.assertAlmostEqual(cmd.target_a, 15.0)
        self.assertAlmostEqual(cmd.target_b, 15.0)

    def test_negative_current_maps_to_charge(self):
        balancer = BatteryBalancer(ramp_rate=100)
        cmd = balancer.calculate(
            BatteryState(soc=20, capacity_kwh=10),
            BatteryState(soc=30, capacity_kwh=10),
            -20,
        )
        self.assertEqual(cmd.discharge_a, 0.0)
        self.assertEqual(cmd.discharge_b, 0.0)
        self.assertGreater(cmd.charge_a, 0.0)
        self.assertGreater(cmd.charge_b, 0.0)


if __name__ == "__main__":
    unittest.main()
