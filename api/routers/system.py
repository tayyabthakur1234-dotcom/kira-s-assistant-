from fastapi import APIRouter
from api.models import (
    VolumeSetRequest, VolumeChangeRequest, BrightnessSetRequest,
    ClipboardSetRequest, WallpaperSetRequest, APIResponse
)
from system.sys_controls import system_controls
from system.info import system_info_provider

router = APIRouter(prefix="/system", tags=["System Controls & Info"])

@router.get("/info", response_model=APIResponse)
def get_system_info():
    """Gathers hardware diagnostics: CPU, RAM, GPU, Disks, Battery, Network, OS."""
    data = system_info_provider.get_system_metrics()
    return APIResponse(status="success", data=data)

@router.post("/volume/set", response_model=APIResponse)
def set_volume(req: VolumeSetRequest):
    """Sets master volume percentage (0-100)."""
    res = system_controls.set_volume(req.level)
    return APIResponse(status="success", data=res)

@router.post("/volume/change", response_model=APIResponse)
def change_volume(req: VolumeChangeRequest):
    """Adjusts volume by delta step."""
    res = system_controls.change_volume(req.delta)
    return APIResponse(status="success", data=res)

@router.post("/volume/mute", response_model=APIResponse)
def mute_volume():
    """Mutes system audio."""
    res = system_controls.mute()
    return APIResponse(status="success", data=res)

@router.post("/volume/unmute", response_model=APIResponse)
def unmute_volume():
    """Unmutes system audio."""
    res = system_controls.unmute()
    return APIResponse(status="success", data=res)

@router.post("/brightness", response_model=APIResponse)
def set_brightness(req: BrightnessSetRequest):
    """Sets display brightness percentage (0-100)."""
    res = system_controls.set_brightness(req.level)
    return APIResponse(status="success", data=res)

@router.get("/clipboard", response_model=APIResponse)
def get_clipboard():
    """Reads current clipboard text content."""
    res = system_controls.get_clipboard()
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/clipboard", response_model=APIResponse)
def set_clipboard(req: ClipboardSetRequest):
    """Sets text content into clipboard."""
    res = system_controls.set_clipboard(req.text)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/wallpaper", response_model=APIResponse)
def set_wallpaper(req: WallpaperSetRequest):
    """Configures desktop wallpaper."""
    res = system_controls.set_wallpaper(req.image_path)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/recycle_bin/empty", response_model=APIResponse)
def empty_recycle_bin():
    """Empties system recycle bin."""
    res = system_controls.empty_recycle_bin()
    return APIResponse(status="success", data=res)
