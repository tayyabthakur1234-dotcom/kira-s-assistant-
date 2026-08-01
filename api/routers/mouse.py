from fastapi import APIRouter
from api.models import (
    MouseMoveRequest, MouseClickRequest, MouseDragRequest,
    MouseScrollRequest, MouseHoverRequest, APIResponse
)
from desktop.mouse import mouse_controller

router = APIRouter(prefix="/mouse", tags=["Mouse Control"])

@router.get("/position", response_model=APIResponse)
def get_cursor_position():
    """Gets the current screen coordinates (x, y) of the mouse cursor."""
    x, y = mouse_controller.get_position()
    return APIResponse(status="success", data={"x": x, "y": y})

@router.post("/move", response_model=APIResponse)
def move_mouse(req: MouseMoveRequest):
    """Moves the mouse cursor smoothly or directly to specified coordinates."""
    res = mouse_controller.move_to(x=req.x, y=req.y, smooth=req.smooth, duration=req.duration)
    return APIResponse(status="success", data=res)

@router.post("/click", response_model=APIResponse)
def click_mouse(req: MouseClickRequest):
    """Executes mouse clicks (left, right, middle, single, double, multi)."""
    res = mouse_controller.click(x=req.x, y=req.y, button=req.button, clicks=req.clicks, interval=req.interval)
    return APIResponse(status="success", data=res)

@router.post("/drag", response_model=APIResponse)
def drag_and_drop(req: MouseDragRequest):
    """Drags mouse from start coordinates and drops at target end coordinates."""
    res = mouse_controller.drag_and_drop(
        start_x=req.start_x, start_y=req.start_y,
        end_x=req.end_x, end_y=req.end_y,
        button=req.button, duration=req.duration
    )
    return APIResponse(status="success", data=res)

@router.post("/scroll", response_model=APIResponse)
def scroll_mouse(req: MouseScrollRequest):
    """Scrolls mouse wheel up or down."""
    res = mouse_controller.scroll(clicks=req.clicks, x=req.x, y=req.y)
    return APIResponse(status="success", data=res)

@router.post("/hover", response_model=APIResponse)
def hover_mouse(req: MouseHoverRequest):
    """Hovers over specified coordinates for a given duration."""
    res = mouse_controller.hover(x=req.x, y=req.y, duration=req.duration)
    return APIResponse(status="success", data=res)
