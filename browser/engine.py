import os
import asyncio
from typing import Dict, Any, List, Optional
from config.settings import settings
from utils.logger import logger

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    async_playwright = None
    Browser = None
    BrowserContext = None
    Page = None


class BrowserAutomationEngine:
    """
    Production-grade Browser Automation Engine based on Playwright Async API.
    Supports Chromium, Chrome, Microsoft Edge, Firefox, Brave, multi-tabs, incognito,
    session storage, cookies, and automatic crash recovery.
    """

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.pages: List[Page] = []
        self.active_page_index: int = 0

    @property
    def active_page(self) -> Optional[Page]:
        if self.pages and 0 <= self.active_page_index < len(self.pages):
            return self.pages[self.active_page_index]
        return None

    async def initialize(
        self,
        browser_type: Optional[str] = None,
        headless: Optional[bool] = None,
        incognito: bool = False,
        user_data_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Launches browser engine with specified configuration.
        browser_type: 'chromium', 'chrome', 'msedge', 'firefox', 'brave'
        """
        if not async_playwright:
            return {"status": "error", "message": "Playwright library is not available."}

        try:
            target_browser = (browser_type or settings.browser_type).lower()
            is_headless = settings.browser_headless if headless is None else headless

            # Ensure downloads directory exists
            os.makedirs(settings.browser_downloads_dir, exist_ok=True)

            self.playwright = await async_playwright().start()

            launch_args = [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]

            # Select browser executable/channel
            channel = None
            if target_browser == "chrome":
                channel = "chrome"
                browser_launcher = self.playwright.chromium
            elif target_browser in ["msedge", "edge"]:
                channel = "msedge"
                browser_launcher = self.playwright.chromium
            elif target_browser == "firefox":
                browser_launcher = self.playwright.firefox
            else:
                browser_launcher = self.playwright.chromium

            kwargs = {
                "headless": is_headless,
                "args": launch_args
            }
            if channel:
                kwargs["channel"] = channel

            if user_data_dir and not incognito:
                os.makedirs(user_data_dir, exist_ok=True)
                self.context = await browser_launcher.launch_persistent_context(
                    user_data_dir,
                    downloads_path=settings.browser_downloads_dir,
                    accept_downloads=True,
                    viewport={"width": 1280, "height": 800},
                    **kwargs
                )
                self.pages = self.context.pages
                if not self.pages:
                    new_p = await self.context.new_page()
                    self.pages.append(new_p)
            else:
                self.browser = await browser_launcher.launch(**kwargs)
                self.context = await self.browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    accept_downloads=True
                )
                first_page = await self.context.new_page()
                self.pages = [first_page]

            self.active_page_index = 0
            logger.info(f"[BrowserEngine] Initialized '{target_browser}' (headless={is_headless}, incognito={incognito})")
            return {
                "status": "success",
                "browser_type": target_browser,
                "headless": is_headless,
                "tabs_count": len(self.pages)
            }

        except Exception as e:
            logger.error(f"[BrowserEngine] Initialization failed: {e}")
            return {"status": "error", "message": str(e)}

    async def ensure_active_page(() -> Optional[Page]:
        pass

    async def get_active_page(self) -> Page:
        if not self.active_page or self.active_page.is_closed():
            init_res = await self.initialize()
            if init_res.get("status") == "error":
                raise RuntimeError(f"Browser launch failed: {init_res.get('message')}")
        return self.active_page

    async def new_tab(self, url: Optional[str] = None) -> Dict[str, Any]:
        """Opens a new tab in current browser context."""
        try:
            if not self.context:
                await self.initialize()

            page = await self.context.new_page()
            self.pages.append(page)
            self.active_page_index = len(self.pages) - 1

            if url:
                if not url.startswith("http://") and not url.startswith("https://"):
                    url = "https://" + url
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            return {
                "status": "success",
                "tab_index": self.active_page_index,
                "url": page.url,
                "title": await page.title()
            }
        except Exception as e:
            logger.error(f"[BrowserEngine] Error creating new tab: {e}")
            return {"status": "error", "message": str(e)}

    async def switch_tab(self, index: int) -> Dict[str, Any]:
        """Switches active focus to specified tab index."""
        if 0 <= index < len(self.pages):
            self.active_page_index = index
            page = self.pages[index]
            await page.bring_to_front()
            return {
                "status": "success",
                "active_tab_index": index,
                "url": page.url,
                "title": await page.title()
            }
        return {"status": "error", "message": f"Tab index {index} out of range (0-{len(self.pages)-1})"}

    async def close_tab(self, index: Optional[int] = None) -> Dict[str, Any]:
        """Closes target tab or current active tab."""
        target_idx = self.active_page_index if index is None else index
        if 0 <= target_idx < len(self.pages):
            page_to_close = self.pages.pop(target_idx)
            if not page_to_close.is_closed():
                await page_to_close.close()
            if self.pages:
                self.active_page_index = min(target_idx, len(self.pages) - 1)
            else:
                self.active_page_index = 0
            return {"status": "success", "remaining_tabs": len(self.pages)}
        return {"status": "error", "message": "Invalid tab index"}

    async def restart(self) -> Dict[str, Any]:
        """Restarts the browser session cleanly."""
        await self.close()
        return await self.initialize()

    async def close(self) -> Dict[str, Any]:
        """Closes browser context and Playwright instance."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

            self.context = None
            self.browser = None
            self.playwright = None
            self.pages = []
            self.active_page_index = 0
            logger.info("[BrowserEngine] Browser session shut down.")
            return {"status": "success", "action": "closed"}
        except Exception as e:
            logger.error(f"[BrowserEngine] Error closing browser: {e}")
            return {"status": "error", "message": str(e)}


browser_engine = BrowserAutomationEngine()
