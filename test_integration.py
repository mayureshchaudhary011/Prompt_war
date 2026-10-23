import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data.get("status") == "online", f"Expected status 'online', got {data.get('status')}"
    assert "AEGIS-Grid" in data.get("system", "")
    print("PASS: Health check returned status: online")

def test_triage_with_pii_flood():
    telemetry = (
        "CRITICAL: Dam breach at Sector-4 Valley reservoir. Water height 12.5 meters with flow rate 450 m3/s. "
        "Contact Director David at 555-438-9201 or d.miller@emergency.gov. SSN: 987-65-4321."
    )
    response = client.post("/api/agent/triage", json={"telemetry_text": telemetry})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    # Verify PII masking
    assert data["pii_redacted"] is True
    assert "555-438-9201" not in data["sanitized_input"]
    assert "d.miller@emergency.gov" not in data["sanitized_input"]
    assert "987-65-4321" not in data["sanitized_input"]
    assert "[REDACTED PHONE]" in data["sanitized_input"]
    assert "[REDACTED EMAIL]" in data["sanitized_input"]
    assert "[REDACTED ID]" in data["sanitized_input"]
    
    # Verify deterministic tool execution
    assert data["tool_call_executed"] == "calculate_flood_risk"
    tool_out = data["tool_output"]
    assert tool_out["risk_level"] == "CRITICAL"
    assert tool_out["wave_velocity_ms"] > 8.0
    
    # Verify HITL gate requirement
    assert data["requires_hitl_approval"] is True
    assert data["action_id"].startswith("ACT-")
    print(f"PASS: Triage executed with PII masking, tool execution, and Action ID: {data['action_id']}")
    return data["action_id"]

def test_triage_power_grid():
    telemetry = "GRID ALERT: Sector-Grid-North overload 940 MW. Grid operator phone 555-882-1920."
    response = client.post("/api/agent/triage", json={"telemetry_text": telemetry})
    assert response.status_code == 200
    data = response.json()
    assert data["tool_call_executed"] == "optimize_power_grid"
    assert data["tool_output"]["trigger_backup_generators"] is True
    assert data["tool_output"]["load_shed_required_mw"] > 0
    print("PASS: Power grid triage executed properly")

def test_hitl_approval_flow(action_id):
    approval_payload = {
        "action_id": action_id,
        "approved": True,
        "approver_id": "OFFICER-COMMANDER-01"
    }
    response = client.post("/api/agent/approve", json=approval_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APPROVED_AND_DISPATCHED"
    assert data["action_id"] == action_id
    assert "SIG-HITL-" in data["audit_signature"]
    print(f"PASS: HITL Approval verified with audit signature: {data['audit_signature']}")

if __name__ == "__main__":
    test_health_check()
    action_id = test_triage_with_pii_flood()
    test_triage_power_grid()
    test_hitl_approval_flow(action_id)
    print("ALL INTEGRATION TESTS PASSED (100%)")
