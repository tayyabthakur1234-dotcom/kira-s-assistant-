from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from utils.logger import logger

from api.routers import (
    mouse, keyboard, window, apps, file, system, power, display,
    cmd, vision, browser, voice, memory, planner, plugins, mcp,
    router as ai_router, agents as ai_agents, dev as dev_router,
    production as production_router
)
import plugins.default_plugins  # Automatically loads and registers default plugins

app = FastAPI(
    title="KIRA AI OS Engine",
    version=settings.version,
    description="KIRA AI - Unified Production AI Operating System (Desktop, Vision, Browser, Voice, Memory, DAG Planner, Plugins, MCP, AI Model Router, Developer Intelligence & Phase 12 Enterprise Platform)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local or remote UI clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(mouse.router)
app.include_router(keyboard.router)
app.include_router(window.router)
app.include_router(apps.router)
app.include_router(file.router)
app.include_router(system.router)
app.include_router(power.router)
app.include_router(display.router)
app.include_router(cmd.router)
app.include_router(vision.router)
app.include_router(browser.router)
app.include_router(voice.router)
app.include_router(memory.router)
app.include_router(planner.router)
app.include_router(plugins.router)
app.include_router(mcp.router)
app.include_router(ai_router.router)
app.include_router(ai_agents.router)
app.include_router(dev_router.router)
app.include_router(production_router.router)

@app.get("/", tags=["Health Check"])
def root_status():
    return {
        "engine": "KIRA AI OS Engine",
        "phase": "Phase 12 - Production Deployment & Enterprise Platform",
        "version": settings.version,
        "status": "online",
        "docs_url": "/docs"
    }



if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.app_name} on {settings.host}:{settings.port}")
    uvicorn.run("api.main:app", host=settings.host, port=settings.port, reload=settings.debug)
