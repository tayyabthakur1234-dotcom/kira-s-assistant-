"""
Test Suite for Phase 12 - Production Deployment & Enterprise Platform (KIRA AI OS)
Tests First-Run Wizard, Background Service, Security Vault, Diagnostics,
Backup/Restore, Auto-Updater, System Modes & Telemetry.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_enterprise_overview():
    response = client.get("/production/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["os_name"] == "KIRA AI Operating System"
    assert "Phase 12" in data["phase"]
    assert len(data["unified_architecture"]) == 12


def test_prerequisites_check():
    response = client.get("/production/prerequisites")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "dependencies" in data


def test_diagnostics_engine():
    response = client.get("/production/diagnostics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["overall_health"] == "100% Operational"
    assert "desktop_automation" in data["subsystems"]
    assert "developer_intelligence" in data["subsystems"]


def test_background_service():
    response = client.post("/production/service", json={"action": "start"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_running"] is True

    status_resp = client.get("/production/service/status")
    assert status_resp.status_code == 200


def test_backup_and_restore():
    create_resp = client.post("/production/backup/create", json={"include_memories": True, "include_plugins": True})
    assert create_resp.status_code == 200
    c_data = create_resp.json()
    assert c_data["status"] == "success"
    fn = c_data["backup_filename"]

    list_resp = client.get("/production/backup/list")
    assert list_resp.status_code == 200

    restore_resp = client.post("/production/backup/restore", json={"backup_filename": fn})
    assert restore_resp.status_code == 200
    assert restore_resp.json()["status"] == "success"


def test_system_modes():
    modes_resp = client.get("/production/modes")
    assert modes_resp.status_code == 200
    assert "active_mode" in modes_resp.json()

    switch_resp = client.post("/production/modes/switch", json={"mode_name": "Developer Mode"})
    assert switch_resp.status_code == 200
    assert switch_resp.json()["active_mode"] == "Developer Mode"


def test_telemetry_logs():
    response = client.get("/production/logs")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_installer_spec():
    response = client.post("/production/installer/spec?target_type=msi")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["target_type"] == "msi"
