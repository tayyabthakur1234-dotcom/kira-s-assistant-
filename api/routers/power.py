from fastapi import APIRouter
from api.models import PowerActionConfirmationRequest, APIResponse
from system.power import power_controls

router = APIRouter(prefix="/power", tags=["Power Controls"])

@router.post("/lock", response_model=APIResponse)
def lock_workstation():
    """Locks workstation session immediately."""
    res = power_controls.lock_session()
    return APIResponse(status="success", data=res)

@router.post("/sleep", response_model=APIResponse)
def sleep_system():
    """Puts system into Sleep mode."""
    res = power_controls.sleep_system()
    return APIResponse(status="success", data=res)

@router.post("/hibernate", response_model=APIResponse)
def hibernate_system():
    """Puts system into Hibernate mode."""
    res = power_controls.hibernate_system()
    return APIResponse(status="success", data=res)

@router.post("/logout", response_model=APIResponse)
def logout_user():
    """Logs off current user session."""
    res = power_controls.logout_user()
    return APIResponse(status="success", data=res)

@router.post("/restart", response_model=APIResponse)
def restart_system(req: PowerActionConfirmationRequest):
    """
    Restarts OS.
    REQUIRES CONFIRMATION: `confirmed: true`.
    """
    res = power_controls.restart_system(confirmed=req.confirmed, timeout_sec=req.timeout_sec)
    return APIResponse(status="success", data=res)

@router.post("/shutdown", response_model=APIResponse)
def shutdown_system(req: PowerActionConfirmationRequest):
    """
    Shuts down OS.
    REQUIRES CONFIRMATION: `confirmed: true`.
    """
    res = power_controls.shutdown_system(confirmed=req.confirmed, timeout_sec=req.timeout_sec)
    return APIResponse(status="success", data=res)
