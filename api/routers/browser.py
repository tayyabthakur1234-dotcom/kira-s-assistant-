from fastapi import APIRouter, HTTPException
from api.models import (
    APIResponse,
    BrowserOpenRequest,
    BrowserOpenURLRequest,
    BrowserSearchRequest,
    BrowserExtractRequest,
    BrowserLoginRequest,
    BrowserUploadRequest,
    BrowserDownloadRequest,
    BrowserGitHubRequest,
    BrowserYouTubeRequest
)
from browser.engine import browser_engine
from browser.navigation import navigation_manager
from browser.search import google_search_engine
from browser.page_analyzer import page_analyzer
from browser.form_filling import form_filling_engine
from browser.ai_navigator import ai_browser_navigator
from browser.github_automation import github_automation
from browser.youtube_automation import youtube_automation
from utils.logger import logger

router = APIRouter(prefix="/browser", tags=["Browser Intelligence Engine"])

@router.post("/open", response_model=APIResponse)
async def open_browser_endpoint(req: BrowserOpenRequest):
    """
    Open or initialize browser instance (Chrome, Microsoft Edge, Firefox, Chromium).
    """
    try:
        res = await browser_engine.initialize(
            browser_type=req.browser_type,
            headless=req.headless,
            incognito=req.incognito
        )
        return APIResponse(
            status=res.get("status", "success"),
            message=f"Browser initialized: {req.browser_type}",
            data=res
        )
    except Exception as e:
        logger.error(f"Error opening browser: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/close", response_model=APIResponse)
async def close_browser_endpoint():
    """
    Close active browser session cleanly.
    """
    try:
        res = await browser_engine.close()
        return APIResponse(
            status="success",
            message="Browser session closed.",
            data=res
        )
    except Exception as e:
        logger.error(f"Error closing browser: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/open_url", response_model=APIResponse)
async def open_url_endpoint(req: BrowserOpenURLRequest):
    """
    Navigate active tab or new tab to specified web URL.
    """
    try:
        res = await navigation_manager.open_url(url=req.url, new_tab=req.new_tab)
        return APIResponse(
            status=res.get("status", "success"),
            message=f"Navigated to {req.url}",
            data=res
        )
    except Exception as e:
        logger.error(f"Error opening URL {req.url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=APIResponse)
async def search_endpoint(req: BrowserSearchRequest):
    """
    Execute Google Search query. Optionally auto-open top organic result.
    """
    try:
        if req.open_first:
            res = await google_search_engine.open_first_result(req.query)
        else:
            res = await google_search_engine.search(req.query)

        return APIResponse(
            status=res.get("status", "success"),
            message=f"Google search for '{req.query}' completed.",
            data=res
        )
    except Exception as e:
        logger.error(f"Error executing browser search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract", response_model=APIResponse)
async def extract_endpoint(req: BrowserExtractRequest):
    """
    Extract structured webpage elements, clean text, tables, forms, links, or Markdown export.
    """
    try:
        ext_type = req.extract_type.lower()
        if ext_type == "text":
            data = await page_analyzer.extract_text()
        elif ext_type == "markdown":
            data = await page_analyzer.export_markdown()
        else:
            data = await page_analyzer.analyze_page()

        return APIResponse(
            status="success",
            message=f"Web content extraction ({ext_type}) completed.",
            data=data
        )
    except Exception as e:
        logger.error(f"Error extracting webpage content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=APIResponse)
async def login_endpoint(req: BrowserLoginRequest):
    """
    Perform web login on specified authentication page.
    """
    try:
        open_res = await navigation_manager.open_url(req.url)
        if open_res.get("status") == "error":
            return APIResponse(status="error", message=open_res.get("message"), data=open_res)

        fill_res = await form_filling_engine.fill_form(
            field_values={"username": req.username, "password": req.password},
            submit_selector="button[type='submit'], input[type='submit']"
        )

        return APIResponse(
            status="success",
            message="Login credentials submitted.",
            data=fill_res
        )
    except Exception as e:
        logger.error(f"Error performing browser login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=APIResponse)
async def upload_endpoint(req: BrowserUploadRequest):
    """
    Upload local file to file input DOM element.
    """
    try:
        res = await form_filling_engine.upload_file(selector=req.selector, file_path=req.file_path)
        return APIResponse(
            status=res.get("status", "success"),
            message="File upload completed.",
            data=res
        )
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download", response_model=APIResponse)
async def download_endpoint(req: BrowserDownloadRequest):
    """
    Trigger download and verify saved file in downloads folder.
    """
    try:
        res = await form_filling_engine.download_file_click(
            download_trigger_selector=req.download_trigger_selector,
            custom_filename=req.custom_filename
        )
        return APIResponse(
            status=res.get("status", "success"),
            message="Download process completed.",
            data=res
        )
    except Exception as e:
        logger.error(f"Error processing download: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/github", response_model=APIResponse)
async def github_endpoint(req: BrowserGitHubRequest):
    """
    Execute GitHub automation tasks (create_repo, clone, create_issue, read_prs).
    """
    try:
        act = req.action.lower()
        if act == "create_repo":
            data = await github_automation.create_repository(
                repo_name=req.repo_url_or_name or "kira-auto-repo",
                description=req.description or ""
            )
        elif act == "clone":
            data = github_automation.clone_repository(repo_url=req.repo_url_or_name or "")
        elif act == "create_issue":
            data = await github_automation.create_issue(
                repo_owner_name=req.repo_url_or_name or "",
                title=req.title or "New issue",
                body=req.body or ""
            )
        elif act == "read_prs":
            data = await github_automation.read_pull_requests(repo_owner_name=req.repo_url_or_name or "")
        else:
            data = {"error": f"Unsupported GitHub action: {req.action}"}

        return APIResponse(
            status="success",
            message=f"GitHub action '{req.action}' executed.",
            data=data
        )
    except Exception as e:
        logger.error(f"Error in GitHub endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/youtube", response_model=APIResponse)
async def youtube_endpoint(req: BrowserYouTubeRequest):
    """
    Execute YouTube automation tasks (search, play, pause, transcript).
    """
    try:
        act = req.action.lower()
        if act == "search":
            data = await youtube_automation.search(req.query_or_url or "")
        elif act == "play":
            data = await youtube_automation.play_video(req.query_or_url or "")
        elif act == "pause":
            data = await youtube_automation.toggle_pause()
        elif act == "transcript":
            data = await youtube_automation.extract_transcript()
        else:
            data = {"error": f"Unsupported YouTube action: {req.action}"}

        return APIResponse(
            status="success",
            message=f"YouTube action '{req.action}' executed.",
            data=data
        )
    except Exception as e:
        logger.error(f"Error in YouTube endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context", response_model=APIResponse)
async def browser_context_endpoint():
    """
    Retrieve active browser context: URL, page title, tab count, history sample, and bookmarks.
    """
    try:
        page = await browser_engine.get_active_page()
        page_analysis = await page_analyzer.analyze_page()

        return APIResponse(
            status="success",
            message="Browser context snapshot retrieved.",
            data={
                "current_url": page.url,
                "current_title": await page.title(),
                "tabs_count": len(browser_engine.pages),
                "active_tab_index": browser_engine.active_page_index,
                "bookmarks": navigation_manager.get_bookmarks(),
                "history_sample": navigation_manager.get_history(limit=5),
                "page_structure": page_analysis
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving browser context: {e}")
        raise HTTPException(status_code=500, detail=str(e))
