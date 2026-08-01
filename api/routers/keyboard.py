from fastapi import APIRouter
from api.models import TypeTextRequest, PressKeyRequest, HotkeyRequest, APIResponse
from desktop.keyboard import keyboard_controller

router = APIRouter(prefix="/keyboard", tags=["Keyboard Automation"])

@router.post("/type", response_model=APIResponse)
def type_text(req: TypeTextRequest):
    """Types out string sequence."""
    res = keyboard_controller.type_text(text=req.text, interval=req.interval)
    return APIResponse(status="success", data=res)

@router.post("/press", response_model=APIResponse)
def press_key(req: PressKeyRequest):
    """Presses single key one or multiple times."""
    res = keyboard_controller.press_key(key=req.key, presses=req.presses)
    return APIResponse(status="success", data=res)

@router.post("/hotkey", response_model=APIResponse)
def execute_hotkey(req: HotkeyRequest):
    """Executes hotkey combo (e.g. ['ctrl', 'c'] or 'ctrl+alt+del')."""
    res = keyboard_controller.execute_hotkey(keys=req.keys)
    return APIResponse(status="success", data=res)

@router.post("/copy", response_model=APIResponse)
def copy_shortcut():
    """Executes Ctrl+C."""
    res = keyboard_controller.copy()
    return APIResponse(status="success", data=res)

@router.post("/paste", response_model=APIResponse)
def paste_shortcut():
    """Executes Ctrl+V."""
    res = keyboard_controller.paste()
    return APIResponse(status="success", data=res)

@router.post("/undo", response_model=APIResponse)
def undo_shortcut():
    """Executes Ctrl+Z."""
    res = keyboard_controller.undo()
    return APIResponse(status="success", data=res)

@router.post("/redo", response_model=APIResponse)
def redo_shortcut():
    """Executes Ctrl+Y."""
    res = keyboard_controller.redo()
    return APIResponse(status="success", data=res)
