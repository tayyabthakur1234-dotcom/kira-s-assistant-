from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "KIRA AI Desktop Control Engine"
    version: str = "1.0.0"
    host: str = Field(default="0.0.0.0", env="KIRA_HOST")
    port: int = Field(default=8000, env="KIRA_PORT")
    debug: bool = Field(default=True, env="KIRA_DEBUG")
    require_confirmation: bool = Field(default=True, env="KIRA_REQUIRE_CONFIRMATION")
    human_mouse_speed: float = Field(default=0.3, env="KIRA_HUMAN_MOUSE_SPEED")
    log_level: str = Field(default="INFO", env="KIRA_LOG_LEVEL")
    log_dir: str = Field(default="logs", env="KIRA_LOG_DIR")

    # Vision & Screen Intelligence Settings
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    vision_local_only: bool = Field(default=False, env="KIRA_VISION_LOCAL_ONLY")
    ocr_engine_preference: str = Field(default="auto", env="KIRA_OCR_ENGINE")
    tesseract_cmd: Optional[str] = Field(default=None, env="TESSERACT_CMD")
    confidence_threshold: float = Field(default=0.6, env="KIRA_VISION_CONFIDENCE_THRESHOLD")

    # Browser Intelligence Settings
    browser_type: str = Field(default="chromium", env="KIRA_BROWSER_TYPE") # chromium, msedge, firefox, chrome
    browser_headless: bool = Field(default=True, env="KIRA_BROWSER_HEADLESS")
    browser_downloads_dir: str = Field(default="downloads", env="KIRA_BROWSER_DOWNLOADS_DIR")
    browser_user_data_dir: Optional[str] = Field(default=None, env="KIRA_BROWSER_USER_DATA_DIR")

    # Phase 4 Voice Intelligence Settings
    wake_word: str = Field(default="Hey Kira", env="KIRA_WAKE_WORD")
    wake_sensitivity: float = Field(default=0.5, env="KIRA_WAKE_SENSITIVITY")
    voice_engine: str = Field(default="kokoro", env="KIRA_VOICE_ENGINE") # kokoro, piper
    voice_profile: str = Field(default="female_1", env="KIRA_VOICE_PROFILE")
    stt_model: str = Field(default="base", env="KIRA_STT_MODEL") # tiny, base, small, medium
    audio_sample_rate: int = Field(default=16000, env="KIRA_AUDIO_SAMPLE_RATE")
    audio_device_index: Optional[int] = Field(default=None, env="KIRA_AUDIO_DEVICE_INDEX")

    # Phase 5 Memory & Autonomous Planner Settings
    db_path: str = Field(default="kira_memory.db", env="KIRA_DB_PATH")
    vector_db_dir: str = Field(default="kira_vector_db", env="KIRA_VECTOR_DB_DIR")
    memory_decay_days: int = Field(default=30, env="KIRA_MEMORY_DECAY_DAYS")
    auto_extract_memory: bool = Field(default=True, env="KIRA_AUTO_EXTRACT_MEMORY")
    max_planner_retries: int = Field(default=3, env="KIRA_MAX_PLANNER_RETRIES")

    # Phase 6 Plugin Platform & MCP Settings
    plugins_dir: str = Field(default="plugins", env="KIRA_PLUGINS_DIR")
    plugin_sandbox_enabled: bool = Field(default=True, env="KIRA_PLUGIN_SANDBOX")
    plugin_auto_reload: bool = Field(default=True, env="KIRA_PLUGIN_AUTO_RELOAD")
    mcp_config_path: str = Field(default="mcp_config.json", env="KIRA_MCP_CONFIG_PATH")


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
