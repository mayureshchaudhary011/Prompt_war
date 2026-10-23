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

    def test_pii_redaction_ssn(self):
        raw_text = "Citizen ID 123-45-6789 trapped on 2nd floor roof."
        sanitized = sanitize_input(raw_text)
        self.assertNotIn("123-45-6789", sanitized)
        self.assertIn("[REDACTED ID]", sanitized)

    def test_hydraulic_tool_calculation(self):
        result = calculate_flood_risk(water_height_meters=10.0, flow_rate_m3s=500.0, sector_id="Sector-9")
        self.assertEqual(result["sector_id"], "Sector-9")
        self.assertGreater(result["wave_velocity_ms"], 0)
        self.assertIn(result["risk_level"], ["CRITICAL", "WARNING", "NORMAL"])
        self.assertTrue(isinstance(result["recommended_evacuation"], bool))

    def test_power_grid_optimization(self):
        result = optimize_power_grid(current_load_mw=950.0, peak_capacity_mw=1000.0, sector_id="Grid-North")
        self.assertTrue(result["trigger_backup_generators"])
        self.assertGreater(result["load_shed_required_mw"], 0)
        self.assertEqual(result["sector_id"], "Grid-North")

    def test_deterministic_triage_decision(self):
        normal_flood = calculate_flood_risk(water_height_meters=1.0, flow_rate_m3s=50.0, sector_id="Sector-1")
        self.assertEqual(normal_flood["risk_level"], "NORMAL")
        self.assertFalse(normal_flood["recommended_evacuation"])

if __name__ == "__main__":
    unittest.main()
