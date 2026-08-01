from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

# Common Base Response
class APIResponse(BaseModel):
    status: str = Field(..., example="success")
    message: Optional[str] = Field(None, example="Operation completed successfully")
    data: Optional[Dict[str, Any]] = None

# Mouse Models
class MouseMoveRequest(BaseModel):
    x: int = Field(..., description="Target X coordinate")
    y: int = Field(..., description="Target Y coordinate")
    smooth: bool = Field(default=True, description="Enable human-like smooth movement")
    duration: Optional[float] = Field(default=None, description="Movement duration in seconds")

class MouseClickRequest(BaseModel):
    x: Optional[int] = Field(None, description="Optional X coordinate")
    y: Optional[int] = Field(None, description="Optional Y coordinate")
    button: str = Field(default="left", description="Button: 'left', 'right', 'middle'")
    clicks: int = Field(default=1, description="Number of clicks")
    interval: float = Field(default=0.1, description="Interval between clicks in seconds")

class MouseDragRequest(BaseModel):
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    button: str = Field(default="left")
    duration: float = Field(default=0.5)

class MouseScrollRequest(BaseModel):
    clicks: int = Field(..., description="Scroll ticks: positive for up, negative for down")
    x: Optional[int] = None
    y: Optional[int] = None

class MouseHoverRequest(BaseModel):
    x: int
    y: int
    duration: float = Field(default=0.5)

# Keyboard Models
class TypeTextRequest(BaseModel):
    text: str = Field(..., description="Text string to type")
    interval: float = Field(default=0.02, description="Delay between key presses")

class PressKeyRequest(BaseModel):
    key: str = Field(..., description="Target key name (e.g. 'enter', 'tab', 'a')")
    presses: int = Field(default=1)

class HotkeyRequest(BaseModel):
    keys: Union[List[str], str] = Field(..., description="List of keys (e.g. ['ctrl', 'c']) or string ('ctrl+alt+del')")

# Window Models
class WindowTargetRequest(BaseModel):
    identifier: Union[int, str] = Field(..., description="HWND handle (int) or title substring (str)")

class WindowMoveResizeRequest(BaseModel):
    identifier: Union[int, str]
    x: int
    y: int
    width: int
    height: int

# Application Models
class AppLaunchRequest(BaseModel):
    command_or_path: str = Field(..., description="Executable path or command name")
    args: Optional[List[str]] = Field(default=None, description="Command line arguments")

class AppCloseRequest(BaseModel):
    identifier: Union[int, str] = Field(..., description="Process PID (int) or process name (str)")
    force: bool = Field(default=False, description="Force kill process")

class AppRestartRequest(BaseModel):
    command_or_path: str
    identifier: Union[int, str]

# File Explorer Models
class FolderOpenRequest(BaseModel):
    folder_path: str

class FolderCreateRequest(BaseModel):
    path: str

class FileCopyMoveRequest(BaseModel):
    src: str
    dst: str

class FileRenameRequest(BaseModel):
    src: str
    new_name: str

class FileSearchRequest(BaseModel):
    root_dir: str
    pattern: str = Field(default="*")

class FileDeleteRequest(BaseModel):
    target_path: str
    confirmed: bool = Field(default=False, description="Explicit user security confirmation")

# System Controls Models
class VolumeSetRequest(BaseModel):
    level: int = Field(..., ge=0, le=100, description="Volume percentage 0-100")

class VolumeChangeRequest(BaseModel):
    delta: int = Field(..., description="Volume change step (+10, -10)")

class BrightnessSetRequest(BaseModel):
    level: int = Field(..., ge=0, le=100, description="Display brightness 0-100")

class ClipboardSetRequest(BaseModel):
    text: str

class WallpaperSetRequest(BaseModel):
    image_path: str

# Power Controls Models
class PowerActionConfirmationRequest(BaseModel):
    confirmed: bool = Field(default=False, description="Explicit user confirmation required for critical operations")
    timeout_sec: int = Field(default=10, description="Delay before executing power command")

# Display Models
class ScreenshotRequest(BaseModel):
    monitor_index: int = Field(default=0)
    region: Optional[Dict[str, int]] = Field(default=None, description="Bounding region {top, left, width, height}")
    save_path: Optional[str] = Field(default=None)

# Command Execution Models
class PowerShellRequest(BaseModel):
    script: str = Field(..., description="PowerShell script block")
    timeout_sec: float = Field(default=30.0)

class CMDRequest(BaseModel):
    command: str = Field(..., description="Windows CMD / Shell command")
    timeout_sec: float = Field(default=30.0)

class PythonExecRequest(BaseModel):
    code: str = Field(..., description="Python 3 source code snippet")
    timeout_sec: float = Field(default=30.0)

# Vision & Screen Intelligence Models
class VisionAnalyzeRequest(BaseModel):
    prompt: Optional[str] = Field(default=None, description="Prompt question for Gemini Vision (e.g. 'What error is shown?')")
    monitor_index: int = Field(default=0)
    region: Optional[Dict[str, int]] = Field(default=None, description="Optional cropping region {top, left, width, height}")

class VisionOCRRequest(BaseModel):
    monitor_index: int = Field(default=0)
    languages: Optional[List[str]] = Field(default=["en", "ur"], description="Languages to recognize e.g. ['en', 'ur']")
    region: Optional[Dict[str, int]] = Field(default=None)

class VisionFindButtonRequest(BaseModel):
    button_text: str = Field(..., description="Button label text to find on screen")
    monitor_index: int = Field(default=0)

class VisionFindTextRequest(BaseModel):
    query_text: str = Field(..., description="Text query to locate on screen")
    monitor_index: int = Field(default=0)

class VisionFindIconRequest(BaseModel):
    icon_name: str = Field(..., description="Name or description of icon to locate")
    monitor_index: int = Field(default=0)

class VisionFindWindowRequest(BaseModel):
    window_title: str = Field(..., description="Window title or app name substring")

class VisionClickTargetRequest(BaseModel):
    target: str = Field(..., description="Button label, text, or visual prompt to locate")
    target_type: str = Field(default="button", description="'button', 'text', 'icon', 'prompt'")
    button: str = Field(default="left", description="Mouse button: 'left', 'right', 'middle'")
    execute_click: bool = Field(default=True, description="Whether to immediately execute Phase 1 mouse click")
    monitor_index: int = Field(default=0)

# Phase 3 Browser Intelligence Models
class BrowserOpenRequest(BaseModel):
    browser_type: Optional[str] = Field(default="chromium", description="'chromium', 'chrome', 'msedge', 'firefox'")
    headless: Optional[bool] = Field(default=True, description="Run browser in headless or headful mode")
    incognito: bool = Field(default=False, description="Enable private incognito session")

class BrowserOpenURLRequest(BaseModel):
    url: str = Field(..., description="URL to open (e.g. 'https://github.com')")
    new_tab: bool = Field(default=False, description="Open URL in a new tab")

class BrowserSearchRequest(BaseModel):
    query: str = Field(..., description="Search query string")
    open_first: bool = Field(default=False, description="Automatically navigate to the first result")

class BrowserExtractRequest(BaseModel):
    extract_type: str = Field(default="all", description="'all', 'text', 'markdown', 'links', 'forms', 'tables'")

class BrowserLoginRequest(BaseModel):
    url: str = Field(..., description="Login page URL")
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password or token")

class BrowserUploadRequest(BaseModel):
    selector: str = Field(..., description="File input DOM selector")
    file_path: str = Field(..., description="Path to local file to upload")

class BrowserDownloadRequest(BaseModel):
    download_trigger_selector: str = Field(..., description="DOM selector of button that triggers download")
    custom_filename: Optional[str] = Field(default=None, description="Optional custom filename to save as")

class BrowserGitHubRequest(BaseModel):
    action: str = Field(..., description="'create_repo', 'clone', 'create_issue', 'read_prs'")
    repo_url_or_name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    body: Optional[str] = Field(default=None)

class BrowserYouTubeRequest(BaseModel):
    action: str = Field(..., description="'search', 'play', 'pause', 'transcript'")
    query_or_url: Optional[str] = Field(default=None)

# Phase 4 Voice Intelligence Models
class VoiceStartRequest(BaseModel):
    wake_word: Optional[str] = Field(default="Hey Kira", description="Wake word trigger string")
    sensitivity: Optional[float] = Field(default=0.5, description="Wake sensitivity threshold (0.1 - 0.9)")
    device_index: Optional[int] = Field(default=None, description="Microphone hardware input device index")

class VoiceSpeakRequest(BaseModel):
    text: str = Field(..., description="Text string to synthesize into voice speech")
    voice_profile: Optional[str] = Field(default="female_1", description="'female_1', 'female_2', 'male_1', 'male_2'")
    speed: Optional[float] = Field(default=1.0, description="Speech playback speed multiplier (0.5 - 2.0)")
    pitch: Optional[float] = Field(default=1.0, description="Voice pitch multiplier (0.5 - 2.0)")
    volume: Optional[float] = Field(default=1.0, description="Speech volume multiplier (0.0 - 1.0)")

class VoiceListenRequest(BaseModel):
    duration_seconds: Optional[float] = Field(default=3.0, description="Microphone recording duration in seconds")

class VoiceWakeWordRequest(BaseModel):
    wake_word: str = Field(..., description="Target wake word string (e.g. 'Hey Kira')")
    sensitivity: float = Field(default=0.5, ge=0.1, le=0.9, description="Wake sensitivity score threshold")

# Phase 5 Memory & Autonomous Agent Models
class MemoryStoreRequest(BaseModel):
    content: str = Field(..., description="Text memory content to store")
    memory_type: str = Field(default="semantic", description="'working', 'conversation', 'long_term', 'semantic', 'procedural', 'project', 'task', 'file', 'preference', 'relationship'")
    category: str = Field(default="general", description="Category tag e.g. 'user_preference', 'user_projects', 'facts'")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata key-value dict")
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance weight rating (0.0 to 1.0)")

class MemorySearchRequest(BaseModel):
    query: str = Field(..., description="Semantic or keyword query text")
    memory_type: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    limit: int = Field(default=5, ge=1, le=50)

class MemoryDeleteRequest(BaseModel):
    memory_id: str = Field(..., description="Memory record ID to delete")

class MemoryUpdateRequest(BaseModel):
    memory_id: str = Field(..., description="Memory record ID to update")
    new_content: str = Field(..., description="Updated memory text string")
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class PlannerCreateRequest(BaseModel):
    goal: str = Field(..., description="High-level goal prompt e.g. 'Build a React website' or 'Install VS Code'")

class PlannerRunRequest(BaseModel):
    plan_id: str = Field(..., description="Plan ID returned by /planner/create")

class PlannerStatusRequest(BaseModel):
    plan_id: str = Field(..., description="Plan ID to query status")

class TaskActionRequest(BaseModel):
    target_id: str = Field(..., description="Plan ID or Task ID")
    action: str = Field(..., description="'pause', 'resume', 'cancel'")



