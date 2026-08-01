from fastapi import APIRouter
from typing import Optional
from api.models import WindowTargetRequest, WindowMoveResizeRequest, APIResponse
from windows.window_manager import window_manager

router = APIRouter(prefix="/window", tags=["Window Manager"])

@router.get("/list", response_model=APIResponse)
def list_windows(query: Optional[str] = None):
    """Lists all visible top-level windows, or filters by query substring."""
    if query:
        wins = window_manager.find_windows(query)
    else:
        wins = window_manager.enumerate_windows()
    return APIResponse(status="success", data={"windows_count": len(wins), "windows": wins})

@router.post("/activate", response_model=APIResponse)
def activate_window(req: WindowTargetRequest):
    """Activates / focuses target window by HWND or title substring."""
    res = window_manager.activate_window(req.identifier)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/minimize", response_model=APIResponse)
def minimize_window(req: WindowTargetRequest):
    """Minimizes target window."""
    res = window_manager.minimize_window(req.identifier)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/maximize", response_model=APIResponse)
def maximize_window(req: WindowTargetRequest):
    """Maximizes target window."""
    res = window_manager.maximize_window(req.identifier)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/restore", response_model=APIResponse)
def restore_window(req: WindowTargetRequest):
    """Restores target window from minimized or maximized state."""
    res = window_manager.restore_window(req.identifier)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/move_resize", response_model=APIResponse)
def move_and_resize_window(req: WindowMoveResizeRequest):
    """Moves and resizes window to specified bounding rectangle."""
    res = window_manager.move_and_resize(req.identifier, req.x, req.y, req.width, req.height)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/close", response_model=APIResponse)
def close_window(req: WindowTargetRequest):
    """Closes target window cleanly."""
    res = window_manager.close_window(req.identifier)
    return APIResponse(status=res.get("status", "success"), data=res)
