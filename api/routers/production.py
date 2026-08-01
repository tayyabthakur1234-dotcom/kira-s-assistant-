"""
FastAPI Router for Phase 12 - Production Deployment & Enterprise Platform
Provides endpoints for First-Run Wizard setup, System Diagnostics, Dependencies Check,
Background Service Control, Auto Updater, Backup/Restore, Security Vault,
Telemetry & Execution Modes.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from production.enterprise_platform import enterprise_platform
from production.installer import installer_engine
from production.first_run_wizard import first_run_wizard
from production.background_service import background_service
from production.auto_updater import auto_updater
from production.crash_recovery import crash_recovery
from production.security_vault import security_vault
from production.backup_restore import backup_manager
from production.diagnostics import diagnostics_engine
from production.telemetry_logging import telemetry_engine
from production.system_modes import system_modes

router = APIRouter(prefix="", tags=["Phase 12 - Production Deployment & Enterprise Platform"])


# Request Models
class OnboardingSetupRequest(BaseModel):
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API Key")
    grok_api_key: Optional[str] = Field(default=None, description="Grok API Key")
    theme: str = Field(default="cyberpunk_dark", description="UI Theme preference")
    language: str = Field(default="en-US", description="Language preference")
    selected_voice: str = Field(default="KIRA Neural Female", description="Default text-to-speech voice")
    microphone_device: str = Field(default="Default System Microphone", description="Audio input device")
    local_ai_enabled: bool = Field(default=True, description="Enable local fallback models")

class ServiceControlRequest(BaseModel):
    action: str = Field(..., description="start | stop | restart | low_resource")

class BackupCreateRequest(BaseModel):
    include_memories: bool = Field(default=True, description="Include Chroma vector DB & graph memories")
    include_plugins: bool = Field(default=True, description="Include installed plugin bundles")

class BackupRestoreRequest(BaseModel):
    backup_filename: str = Field(..., description="Filename of backup archive to restore")

class SystemModeRequest(BaseModel):
    mode_name: str = Field(..., description="Mode name e.g. 'Windows Service Mode', 'Developer Mode', 'Offline Mode'")

class CheckUpdateRequest(BaseModel):
    channel: str = Field(default="stable", description="stable | beta")


# Endpoints

@router.get("/production/overview", summary="Get Phase 12 Enterprise Platform overview and system health status")
async def get_overview():
    return enterprise_platform.get_enterprise_overview()

@router.get("/production/prerequisites", summary="Detect presence of Python, Git, Node, Rust, Playwright, PowerShell & VC++ Runtime")
async def check_prerequisites():
    return installer_engine.detect_system_dependencies()

@router.post("/production/wizard/setup", summary="Complete first-run onboarding wizard setup and save API keys / settings")
async def wizard_setup(req: OnboardingSetupRequest):
    if req.gemini_api_key:
        ver = await first_run_wizard.verify_gemini_api_key(req.gemini_api_key)
        if not ver.get("valid"):
            raise HTTPException(status_code=400, detail=ver.get("message"))
    return await first_run_wizard.complete_onboarding(req.model_dump())

@router.get("/production/diagnostics", summary="Run comprehensive system diagnostics across all 12 Phase engines")
async def run_diagnostics():
    return diagnostics_engine.run_full_diagnostics()

@router.post("/production/service", summary="Control background daemon (start, stop, low resource mode)")
async def control_service(req: ServiceControlRequest):
    if req.action == "start":
        return background_service.start_service()
    elif req.action == "stop":
        return background_service.stop_service()
    elif req.action == "low_resource":
        return background_service.set_low_resource_mode(True)
    return background_service.get_service_status()

@router.get("/production/service/status", summary="Get background service state")
async def get_service_status():
    return background_service.get_service_status()

@router.post("/production/update/check", summary="Check update server for KIRA OS releases and verify SHA-256 integrity")
async def check_update(req: CheckUpdateRequest):
    return await auto_updater.check_for_updates(channel=req.channel)

@router.post("/production/backup/create", summary="Create full encrypted backup archive of settings, memories, and plugins")
async def create_backup(req: BackupCreateRequest):
    return backup_manager.create_backup(
        include_memories=req.include_memories,
        include_plugins=req.include_plugins
    )

@router.get("/production/backup/list", summary="List available state backup archives")
async def list_backups():
    return {"status": "success", "backups": backup_manager.list_backups()}

@router.post("/production/backup/restore", summary="Restore configuration, memory, and plugin state from backup archive")
async def restore_backup(req: BackupRestoreRequest):
    return backup_manager.restore_backup(req.backup_filename)

@router.get("/production/modes", summary="Get active and available system execution modes")
async def get_modes():
    return system_modes.get_mode_status()

@router.post("/production/modes/switch", summary="Switch system execution mode")
async def switch_mode(req: SystemModeRequest):
    return system_modes.set_active_mode(req.mode_name)

@router.get("/production/logs", summary="Get recent audit logs and execution telemetry records")
async def get_telemetry_logs(limit: int = 50, category: Optional[str] = None):
    return {
        "status": "success",
        "logs": telemetry_engine.get_recent_logs(limit=limit, category=category)
    }

@router.post("/production/installer/spec", summary="Generate Windows MSI/EXE/Portable installer spec configurations")
async def get_installer_spec(target_type: str = "msi"):
    return installer_engine.generate_installer_spec(target_type=target_type)
