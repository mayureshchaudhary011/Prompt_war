import unittest
from main import sanitize_input, calculate_flood_risk, optimize_power_grid

class TestAEGISAgent(unittest.TestCase):

    def test_pii_redaction_phone(self):
        raw_text = "Call officer John at 555-123-4567 for Sector 2 updates."
        sanitized = sanitize_input(raw_text)
        self.assertNotIn("555-123-4567", sanitized)
        self.assertIn("[REDACTED PHONE]", sanitized)

    def test_pii_redaction_email(self):
        raw_text = "Report sent to admin@emergency.gov immediately."
        sanitized = sanitize_input(raw_text)
        self.assertNotIn("admin@emergency.gov", sanitized)
        self.assertIn("[REDACTED EMAIL]", sanitized)

    def test_hydraulic_tool_calculation(self):
        result = calculate_flood_risk(water_height_meters=10.0, flow_rate_m3s=500.0, sector_id="Sector-9")
        self.assertEqual(result["sector_id"], "Sector-9")
        self.assertGreater(result["wave_velocity_ms"], 0)
        self.assertIn(result["risk_level"], ["CRITICAL", "WARNING", "NORMAL"])

    def test_power_grid_optimization(self):
        result = optimize_power_grid(current_load_mw=950.0, peak_capacity_mw=1000.0, sector_id="Grid-North")
        self.assertTrue(result["trigger_backup_generators"])
        self.assertGreater(result["load_shed_required_mw"], 0)

if __name__ == "__main__":
    unittest.main()