import time
from typing import Dict, Any, List, Optional
from browser.engine import browser_engine
from utils.logger import logger

class BrowserNavigationManager:
    """
    Browser Navigation, History, Bookmarks, and Tab Orchestration Engine.
    """

    def __init__(self):
        self._history: List[Dict[str, Any]] = []
        self._bookmarks: List[Dict[str, Any]] = []

    async def open_url(self, url: str, new_tab: bool = False) -> Dict[str, Any]:
        """Navigates current active tab or new tab to specified URL."""
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

            if new_tab:
                return await browser_engine.new_tab(url)

            page = await browser_engine.get_active_page()
            logger.info(f"[Navigation] Navigating to: {url}")
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            title = await page.title()
            status_code = response.status if response else 200

            # Record history
            hist_item = {
                "url": url,
                "title": title,
                "timestamp": time.time(),
                "status_code": status_code
            }
            self._history.append(hist_item)

            return {
                "status": "success",
                "url": page.url,
                "title": title,
                "http_status": status_code
            }
        except Exception as e:
            logger.error(f"[Navigation] Failed navigating to {url}: {e}")
            return {"status": "error", "message": str(e), "url": url}

    async def go_back(self) -> Dict[str, Any]:
        """Navigates back in browser history."""
        try:
            page = await browser_engine.get_active_page()
            response = await page.go_back(wait_until="domcontentloaded")
            return {
                "status": "success",
                "url": page.url,
                "title": await page.title(),
                "http_status": response.status if response else 200
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def go_forward(self) -> Dict[str, Any]:
        """Navigates forward in browser history."""
        try:
            page = await browser_engine.get_active_page()
            response = await page.go_forward(wait_until="domcontentloaded")
            return {
                "status": "success",
                "url": page.url,
                "title": await page.title(),
                "http_status": response.status if response else 200
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def refresh(self) -> Dict[str, Any]:
        """Reloads current active page."""
        try:
            page = await browser_engine.get_active_page()
            response = await page.reload(wait_until="domcontentloaded")
            return {
                "status": "success",
                "url": page.url,
                "title": await page.title(),
                "http_status": response.status if response else 200
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def duplicate_tab(self) -> Dict[str, Any]:
        """Duplicates current active tab."""
        try:
            page = await browser_engine.get_active_page()
            curr_url = page.url
            return await browser_engine.new_tab(curr_url)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def add_bookmark(self, title: str, url: str) -> Dict[str, Any]:
        """Saves bookmark item to memory store."""
        bookmark = {"title": title, "url": url, "timestamp": time.time()}
        self._bookmarks.append(bookmark)
        return {"status": "success", "bookmark": bookmark}

    def get_bookmarks(self) -> List[Dict[str, Any]]:
        return self._bookmarks

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._history[-limit:]

navigation_manager = BrowserNavigationManager()
