from fastapi import APIRouter
from typing import Optional
from api.models import AppLaunchRequest, AppCloseRequest, AppRestartRequest, APIResponse
from system.apps import app_manager

router = APIRouter(prefix="/app", tags=["Applications Lifecycle"])

@router.get("/list", response_model=APIResponse)
def list_running_apps(filter: Optional[str] = None):
    """Detects currently running application processes."""
    apps = app_manager.detect_running_apps(filter_name=filter)
    return APIResponse(status="success", data={"running_apps_count": len(apps), "processes": apps})

@router.post("/open", response_model=APIResponse)
def launch_application(req: AppLaunchRequest):
    """Launches application executable or command line."""
    res = app_manager.launch_app(req.command_or_path, args=req.args)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/close", response_model=APIResponse)
def close_application(req: AppCloseRequest):
    """Terminates application process by PID or process name."""
    res = app_manager.close_app(req.identifier, force=req.force)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/restart", response_model=APIResponse)
def restart_application(req: AppRestartRequest):
    """Terminates and re-launches application."""
    res = app_manager.restart_app(req.command_or_path, req.identifier)
    return APIResponse(status="success", data=res)
