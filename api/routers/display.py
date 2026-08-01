from fastapi import APIRouter
from api.models import ScreenshotRequest, APIResponse
from desktop.display import display_manager

router = APIRouter(prefix="/display", tags=["Display & Monitors"])

@router.get("/monitors", response_model=APIResponse)
def get_monitors():
    """Returns resolutions and positions of all connected display monitors."""
    monitors = display_manager.get_monitors_info()
    return APIResponse(status="success", data={"monitors_count": len(monitors), "monitors": monitors})

@router.post("/screenshot", response_model=APIResponse)
def take_screenshot(req: ScreenshotRequest):
    """Captures desktop screenshot on specified monitor index or custom bounding box."""
    res = display_manager.take_screenshot(monitor_index=req.monitor_index, region=req.region, save_path=req.save_path)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/record_sequence", response_model=APIResponse)
def record_sequence(duration_sec: float = 2.0, fps: int = 5):
    """Captures rapid frame sequence interface for vision analysis."""
    res = display_manager.capture_screen_sequence(duration_sec=duration_sec, fps=fps)
    return APIResponse(status="success", data=res)
