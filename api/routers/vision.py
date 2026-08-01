from fastapi import APIRouter, HTTPException
from api.models import (
    APIResponse,
    VisionAnalyzeRequest,
    VisionOCRRequest,
    VisionFindButtonRequest,
    VisionFindTextRequest,
    VisionFindIconRequest,
    VisionFindWindowRequest,
    VisionClickTargetRequest,
    ScreenshotRequest
)
from vision.capture import screen_capture_engine
from vision.ocr_engine import ocrengine
from vision.ui_detector import ui_detector
from vision.gemini_vision import gemini_vision_engine
from vision.visual_search import visual_search_engine
from vision.click_target import click_target_resolver
from vision.app_intelligence import app_intelligence
from vision.error_understanding import error_understanding_engine
from vision.context_tracker import context_tracker
from windows.window_manager import window_manager
from utils.logger import logger

router = APIRouter(prefix="/vision", tags=["Vision Intelligence Engine"])

@router.post("/capture", response_model=APIResponse)
def capture_screen_endpoint(req: ScreenshotRequest):
    """
    Capture screenshot of specified monitor or region. Returns Base64 PNG and metadata.
    """
    try:
        img, metadata = screen_capture_engine.capture_screen(
            monitor_index=req.monitor_index,
            region=req.region
        )
        base64_img = screen_capture_engine.image_to_base64(img)
        metadata["image_base64"] = base64_img

        return APIResponse(
            status="success",
            message="Screen capture completed successfully.",
            data=metadata
        )
    except Exception as e:
        logger.error(f"Error capturing screen: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=APIResponse)
def analyze_screen_endpoint(req: VisionAnalyzeRequest):
    """
    Analyze desktop screen using Gemini Vision AI. Returns structured JSON breakdown.
    """
    try:
        img, capture_meta = screen_capture_engine.capture_screen(
            monitor_index=req.monitor_index,
            region=req.region
        )
        analysis_result = gemini_vision_engine.analyze_screen(img, prompt=req.prompt)
        analysis_result["capture_metadata"] = capture_meta

        return APIResponse(
            status="success",
            message="Screen visual analysis completed.",
            data=analysis_result
        )
    except Exception as e:
        logger.error(f"Error analyzing screen: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ocr", response_model=APIResponse)
def ocr_screen_endpoint(req: VisionOCRRequest):
    """
    Perform multi-language OCR on current screen to extract text with bounding boxes [x, y, w, h].
    """
    try:
        img, capture_meta = screen_capture_engine.capture_screen(
            monitor_index=req.monitor_index,
            region=req.region
        )
        extracted_items = ocrengine.extract_text(img, languages=req.languages)

        return APIResponse(
            status="success",
            message=f"Extracted {len(extracted_items)} text blocks via OCR.",
            data={
                "count": len(extracted_items),
                "text_items": extracted_items,
                "capture_metadata": capture_meta
            }
        )
    except Exception as e:
        logger.error(f"Error performing screen OCR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find_button", response_model=APIResponse)
def find_button_endpoint(req: VisionFindButtonRequest):
    """
    Locate button coordinates on screen matching target text label.
    """
    try:
        img, _ = screen_capture_engine.capture_screen(monitor_index=req.monitor_index)
        match_res = visual_search_engine.find_button(img, req.button_text)

        return APIResponse(
            status="success" if match_res.get("found") else "not_found",
            message=f"Button search for '{req.button_text}' completed.",
            data=match_res
        )
    except Exception as e:
        logger.error(f"Error finding button: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find_text", response_model=APIResponse)
def find_text_endpoint(req: VisionFindTextRequest):
    """
    Locate text coordinates on screen matching target text string.
    """
    try:
        img, _ = screen_capture_engine.capture_screen(monitor_index=req.monitor_index)
        match_res = visual_search_engine.find_text(img, req.query_text)

        return APIResponse(
            status="success" if match_res.get("found") else "not_found",
            message=f"Text search for '{req.query_text}' completed.",
            data=match_res
        )
    except Exception as e:
        logger.error(f"Error finding text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find_icon", response_model=APIResponse)
def find_icon_endpoint(req: VisionFindIconRequest):
    """
    Locate icon coordinates on screen by icon name or description.
    """
    try:
        img, _ = screen_capture_engine.capture_screen(monitor_index=req.monitor_index)
        match_res = visual_search_engine.find_icon(img, req.icon_name)

        return APIResponse(
            status="success" if match_res.get("found") else "not_found",
            message=f"Icon search for '{req.icon_name}' completed.",
            data=match_res
        )
    except Exception as e:
        logger.error(f"Error finding icon: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find_window", response_model=APIResponse)
def find_window_endpoint(req: VisionFindWindowRequest):
    """
    Locate target window handle, title, process, and bounding box coordinates.
    """
    try:
        windows = window_manager.list_windows()
        matching = [
            w for w in windows
            if req.window_title.lower() in w["title"].lower() or req.window_title.lower() in w["app"].lower()
        ]

        if matching:
            target_win = matching[0]
            return APIResponse(
                status="success",
                message=f"Found window matching '{req.window_title}'.",
                data={
                    "found": True,
                    "window": target_win
                }
            )

        return APIResponse(
            status="not_found",
            message=f"No visible window found matching '{req.window_title}'.",
            data={"found": False, "target": req.window_title}
        )
    except Exception as e:
        logger.error(f"Error finding window: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/click_target", response_model=APIResponse)
def click_target_endpoint(req: VisionClickTargetRequest):
    """
    Locate UI target (button/text/icon/prompt), verify confidence, and pass coordinates
    to Phase 1 Desktop Control Engine to perform the click.
    """
    try:
        img, _ = screen_capture_engine.capture_screen(monitor_index=req.monitor_index)
        result = click_target_resolver.resolve_and_click(
            target=req.target,
            target_type=req.target_type,
            image=img,
            button=req.button,
            execute_click=req.execute_click
        )

        return APIResponse(
            status="success" if result.get("found") else "failed",
            message=f"Click target resolution for '{req.target}' completed.",
            data=result
        )
    except Exception as e:
        logger.error(f"Error in click target endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context", response_model=APIResponse)
def vision_context_endpoint():
    """
    Get current context: active focused window, user mouse activity, open application layout, and error diagnostics.
    """
    try:
        img, _ = screen_capture_engine.capture_screen()
        ctx_data = context_tracker.get_current_context()

        active_win_title = ctx_data.get("active_window", {}).get("title", "")
        layout_data = app_intelligence.analyze_app_layout(img, active_app_hint=active_win_title)
        error_data = error_understanding_engine.analyze_errors(img)

        return APIResponse(
            status="success",
            message="Vision context snapshot retrieved.",
            data={
                "tracker_context": ctx_data,
                "app_layout": layout_data,
                "error_diagnostics": error_data
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving vision context: {e}")
        raise HTTPException(status_code=500, detail=str(e))
