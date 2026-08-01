# KIRA AI - Phase 1 to Phase 8: Complete AI Operating System Engine

> **Principal AI Operating System Engine** for KIRA AI OS.
> Production-grade OS control engine featuring human-like desktop automation, real-time computer vision intelligence, autonomous Playwright browser control (Chrome, Edge, Firefox, Brave), JARVIS-like low-latency Voice Intelligence, Phase 5 Long-Term Memory & Autonomous DAG Graph Planning Engine, Phase 6 Plugin & MCP Ecosystem, Phase 7 3D Holographic Anime Avatar + Transparent Electron Desktop Operating System, and **Phase 8 AI Model Router & Multi-Agent Intelligence Engine**.

---

## 🤖 Phase 8 Features: AI Model Router & Multi-Agent Intelligence

- **AI Model Router**: Automatically detects request types (Coding, Reasoning, Vision, Math, Desktop Control, Browser, Planning, Conversation, Research, Creative Writing, Image Analysis, Voice) and selects the optimal model.
- **Supported Models**: Gemini 2.5 Pro, Gemini Flash, Grok 4, OpenAI GPT, Claude, DeepSeek, Qwen, Llama, Mistral, and local Ollama.
- **Automatic Failover & Retry**: Seamless fallback chain if an API fails, switches models automatically without interrupting user tasks.
- **10 Specialized AI Agents**:
  1. **Planner Agent**: Task decomposition, step assignment, DAG scheduling
  2. **Security Agent**: Command safety inspection, permission verification, risk scoring
  3. **Desktop Agent**: Windows UI automation, clicks, typing
  4. **Vision Agent**: Screenshot analysis, button location, OCR
  5. **Browser Agent**: Playwright web navigation, scraping, file download
  6. **Coding Agent**: Code synthesis, debugging, unit tests, documentation
  7. **Memory Agent**: Vector and relational memory management
  8. **Research Agent**: Internet research, summarization, fact verification
  9. **Reasoning Agent**: Mathematical solving and analytical logic
  10. **Plugin Agent**: Sandbox plugins and MCP tool execution
- **Self-Verification Engine**: Automated result verification, error detection, and self-fixing retries.
- **REST API Endpoints**:
  - `POST /router/model`
  - `POST /router/task`
  - `GET /agents/list`
  - `POST /agents/run`
  - `GET /agents/status`
  - `GET /models/status`
  - `POST /models/select`

---

## 🏗️ Phase 7 Architecture & Desktop OS Structure

```
.
├── electron/
│   ├── main.js                # Electron Main Process (Always-on-top, Transparent)
│   └── preload.js             # Secure Context Bridge Preload
├── src/
│   ├── components/
│   │   ├── ThreeAvatar.tsx    # 3D Holographic Particle Anime Avatar (Three.js WebGL)
│   │   ├── OSDashboardModal.tsx # JARVIS Operating System Core Dashboard Hub
│   │   ├── views/             # Integrated Phase 1-7 OS Views
│   │   │   ├── SystemDashboardView.tsx # Hardware Telemetry & System Status
│   │   │   ├── TaskDAGView.tsx       # Autonomous DAG Planning & Task Queue
│   │   │   ├── MemoryView.tsx        # Persistent Memory Engine & Vector Search
│   │   │   ├── PluginMCPView.tsx     # Plugin Ecosystem & MCP Server Console
│   │   │   ├── CommandCenterView.tsx # Neural Terminal & Live Stream Console
│   │   │   └── OverlayControlView.tsx# Desktop Overlays & Glass Framing
├── electron-builder.json      # Windows NSIS Installer & Portable Mode Packaging
```

---

## 📖 Phase 7 Features & 3D Avatar Rendering

- **3D Holographic Anime Avatar**: Real-time Three.js WebGL particle matrix avatar with lip sync driven by audio amplitude, eye tracking cursor movement, blinking, breathing float, listening rings, and state-reactive holographic color glows.
- **Glassmorphic Operating System HUD**: Full telemetry dashboard monitoring CPU, GPU, RAM, Disk, Temperature, Battery, master controls, task queue, and memory vector store.
- **Electron Container Support**: Transparent window framing, click-through mode, desktop overlays, always-on-top mode, and multi-monitor floating HUD.

---

## 🚀 Building & Packaging Desktop Installer

```bash
# Build React & Express Server bundle
npm run build

# Package Electron Application (Windows Installer & Portable executable)
npx electron-builder --win
```


---

## 🏗️ Architecture & Folder Structure

```
.
├── api/
│   ├── main.py                # FastAPI Application Entrypoint
│   ├── models.py              # Pydantic Schemas & Requests
│   └── routers/               # Modular REST API Routers
│       ├── mouse.py           # /mouse/* endpoints
│       ├── keyboard.py        # /keyboard/* endpoints
│       ├── window.py          # /window/* endpoints
│       ├── apps.py            # /app/* endpoints
│       ├── file.py            # /file/* endpoints
│       ├── system.py          # /system/* endpoints
│       ├── power.py           # /power/* endpoints
│       ├── display.py         # /display/* endpoints
│       ├── cmd.py             # /cmd/* endpoints
│       ├── vision.py          # /vision/* endpoints (Phase 2)
│       ├── browser.py         # /browser/* endpoints (Phase 3)
│       └── voice.py           # /voice/* endpoints (Phase 4)
├── voice/                     # Phase 4 - Voice Intelligence Engine
│   ├── audio_input.py         # Streaming Microphone Capture, VAD & Noise Suppression Engine
│   ├── wakeword.py            # openWakeWord "Hey Kira" Detector & Sensitivity Tuning
│   ├── stt_engine.py          # Streaming Faster Whisper STT (English, Hindi, Urdu, Mixed)
│   ├── tts_engine.py          # Kokoro TTS (Primary) & Piper (Fallback) Emotional Synthesis
│   ├── interruption.py       # Barge-In / Interruption Manager for Fluid Dialogue
│   ├── command_router.py      # Automatic Intent Classifier & Phase 1/2/3/AI Dispatcher
│   └── voice_assistant.py     # JARVIS Always-On Voice Loop Orchestrator
├── browser/                   # Phase 3 - Browser Intelligence Engine
│   ├── engine.py              # Playwright Lifecycle, Browsers & Profiles Engine
│   ├── navigation.py          # Tabs, History, Bookmarks & Navigation Engine
│   ├── search.py              # Google Search Engine & Result Parser
│   ├── page_analyzer.py       # DOM Structural Analysis, Forms & Markdown Export
│   ├── form_filling.py        # Form Fills, File Uploads & Download Tracking
│   ├── ai_navigator.py        # AI Navigation & Phase 2 Vision Fallback Engine
│   ├── github_automation.py   # GitHub Repo Creation, Clone, Issues & PR Engine
│   ├── youtube_automation.py  # YouTube Search, Playback, Transcript Engine
│   ├── gmail_automation.py    # Gmail Inbox, Search, Compose & Confirmed Send
│   └── social_automation.py   # X, LinkedIn, Reddit Safe Navigation & Post Engine
├── vision/                    # Phase 2 - Vision Intelligence Modules
│   ├── capture.py             # High-FPS Multi-Monitor Real-Time Capture Engine
│   ├── ocr_engine.py          # EasyOCR & Tesseract Engine (English & Urdu)
│   ├── ui_detector.py         # OpenCV UI Contour Classification Engine
│   ├── gemini_vision.py       # Gemini 3.6 Flash Screen Analysis Engine
│   ├── visual_search.py       # Button, Icon, Text, Color & Template Search Engine
│   ├── click_target.py        # Target Resolver & Phase 1 Click Integration
│   ├── app_intelligence.py    # Application Layout Awareness Engine
│   ├── error_understanding.py # Error Popup & Stack Trace Diagnostics Engine
│   └── context_tracker.py     # Real-Time Context & Activity Tracker Engine
├── config/
│   ├── __init__.py
│   └── settings.py            # Pydantic Environment Settings
├── desktop/
│   ├── mouse.py               # Human-like Mouse Trajectory & Clicking Engine
│   ├── keyboard.py            # Typing, Hotkeys & Shortcut Actions
│   └── display.py             # Resolution & Multi-Monitor Screenshot Capture
├── windows/
│   └── window_manager.py      # Win32 / PyGetWindow Handle & Focus Control
├── system/
│   ├── apps.py                # Process Detection, Launching & Termination
│   ├── file_explorer.py       # File Search, Directory Operations & Delete
│   ├── sys_controls.py        # Volume, Brightness, Clipboard & Wallpaper
│   ├── power.py               # Sleep, Lock, Shutdown & Restart
│   ├── info.py                # CPU, RAM, GPU, Disk, Network Diagnostics
│   └── cmd_executor.py        # PowerShell, CMD & Inline Python Exec
├── utils/
│   ├── logger.py              # Rotating File & Console Logger
│   └── security.py            # Confirmation Security Guard
├── tests/
│   ├── test_engine.py         # Phase 1 PyTest Unit Test Suite
│   ├── test_vision.py         # Phase 2 Vision PyTest Unit Test Suite
│   ├── test_browser.py        # Phase 3 Browser PyTest Unit Test Suite
│   └── test_voice.py          # Phase 4 Voice PyTest Unit Test Suite
├── requirements.txt           # Python 3.12 Dependencies
├── .env.example               # Environment Configuration Blueprint
└── README.md                  # Complete System & Setup Documentation
```

---

## 🚀 Installation Instructions & Windows Setup Guide

### Prerequisites
- **OS**: Windows 10 / Windows 11 (64-bit)
- **Python**: Python 3.12+
- **Privileges**: Administrator privileges recommended.

### Step 1: Clone & Setup Environment
```bash
git clone https://github.com/your-org/kira-ai-engine.git
cd kira-ai-engine

python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies & Playwright Browsers
```bash
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium chrome msedge firefox
```

### Step 3: Configure Environment (.env)
```bash
cp .env.example .env
```

### Step 4: Launch FastAPI Server
```bash
python -m api.main
```
The FastAPI server will be live at `http://localhost:8000`.
Swagger UI documentation: `http://localhost:8000/docs`

---

## 📖 Complete API Reference

### Phase 1 - Desktop Control Engine
| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/mouse/position` | `GET` | Get current cursor (x, y) coordinates |
| `/mouse/move` | `POST` | Smooth or instant move cursor to target |
| `/mouse/click` | `POST` | Execute single, double, right, or middle click |
| `/keyboard/type` | `POST` | Type out character string |
| `/window/activate` | `POST` | Focus / bring window to foreground |
| `/app/open` | `POST` | Launch executable or system command |

### Phase 2 - Vision & Screen Intelligence Engine
| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/vision/capture` | `POST` | Real-time screenshot capture with Base64 PNG |
| `/vision/analyze` | `POST` | Gemini Vision screen analysis returning structured JSON |
| `/vision/ocr` | `POST` | Multi-language OCR (English & Urdu) bounding box extraction |
| `/vision/click_target` | `POST` | Target locator & automated Phase 1 click execution |
| `/vision/context` | `POST` | Real-time app layout, active window & error diagnostics |

### Phase 3 - Browser Intelligence Engine
| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/browser/open` | `POST` | Open or launch browser instance (Chrome, Edge, Firefox) |
| `/browser/close` | `POST` | Cleanly close active browser session |
| `/browser/open_url` | `POST` | Navigate active or new tab to URL |
| `/browser/search` | `POST` | Execute Google Search query & optionally open top result |
| `/browser/extract` | `POST` | Extract structured DOM elements, text, tables, or Markdown |
| `/browser/login` | `POST` | Automated login authentication on webpage |
| `/browser/upload` | `POST` | Upload file to DOM file input element |
| `/browser/download` | `POST` | Trigger file download & verify saved file |
| `/browser/github` | `POST` | Create repo, clone, create issue, or read PRs |
| `/browser/youtube` | `POST` | Search YouTube, play/pause video, or extract transcript |
| `/browser/context` | `POST` | Snapshot browser context, tabs, history & bookmarks |

### Phase 4 - Voice Intelligence Engine (JARVIS-like System)
| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/voice/start` | `POST` | Activate always-on background voice assistant |
| `/voice/stop` | `POST` | Stop / mute voice assistant background loop |
| `/voice/listen` | `POST` | Record microphone input & transcribe to text |
| `/voice/speak` | `POST` | Synthesize and play emotional voice speech (Kokoro/Piper) |
| `/voice/status` | `POST` | Get voice status, active mic list & voice profiles |
| `/voice/wakeword` | `POST` | Configure target wake word ("Hey Kira") & sensitivity |
| `/voice/ws` | `WebSocket` | Real-time bidirectional streaming audio & speech socket |

### Phase 5 - Memory & Autonomous Agent Engine
| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/memory/store` | `POST` | Store structured memory entry in SQLite and Vector index |
| `/memory/search` | `POST` | Semantic vector search across memories |
| `/memory/delete` | `POST` | Delete memory record by ID across database and vector store |
| `/memory/update` | `POST` | Update memory text and re-index vector embeddings |
| `/memory/export` | `POST` | Export complete memory footprint to JSON |
| `/memory/forget` | `POST` | Automatic decay & cleanup of low-value stale memories |
| `/planner/create` | `POST` | Decompose high-level goal into an actionable DAG sub-task plan |
| `/planner/run` | `POST` | Execute plan sub-tasks autonomously across Phase 1-4 engines |
| `/planner/status` | `POST` | Get real-time progress, completion %, and sub-task list |
| `/tasks/list` | `POST` | List all active sub-tasks across registered plans |
| `/tasks/action` | `POST` | Perform control actions (`pause`, `resume`, `cancel`) |

### Phase 6 - Plugin Platform & MCP Integration System
| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/plugins/install` | `POST` | Install or activate plugin from marketplace catalog |
| `/plugins/remove` | `POST` | Uninstall and remove plugin from active registry |
| `/plugins/list` | `GET/POST` | List installed plugins and marketplace catalog |
| `/plugins/update` | `POST` | Reload or update plugin configuration |
| `/plugins/enable` | `POST` | Enable registered plugin |
| `/plugins/disable` | `POST` | Disable registered plugin |
| `/plugins/health` | `GET/POST` | Perform plugin ecosystem health diagnostic check |
| `/plugins/execute` | `POST` | Execute plugin action inside security sandbox |
| `/mcp/connect` | `POST` | Connect external MCP server & discover tools |
| `/mcp/tools` | `GET/POST` | List discovered & exported MCP tools |
| `/mcp/run` | `POST` | Execute tool on connected MCP server |
| `/mcp/jsonrpc` | `POST` | JSON-RPC 2.0 endpoint exposing KIRA OS as an MCP Server |



---

## 🔒 Security & Mute Confirmation Policy

1. **Wake Word Triggering**: Microphone stream is processed locally for wake word detection ("Hey Kira"). Recording is never saved continuously.
2. **Push-to-Mute**: `/voice/stop` endpoint instantly mutes microphone and disarms listening.
3. **Critical Confirmation**: Deletions (`POST /file/delete`), Power actions (`POST /power/*`), Emails (`POST /browser/gmail`), and Social updates (`POST /browser/social`) strictly require explicit `confirmed: true`.

---

## 🧪 Running Unit Tests

```bash
pytest tests/ -v
```
