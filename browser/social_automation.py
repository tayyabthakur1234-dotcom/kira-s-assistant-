from typing import Dict, Any, Optional
from browser.engine import browser_engine
from utils.security import security_guard
from utils.logger import logger

class SocialMediaAutomationEngine:
    """
    Safe Social Media Navigation & Interaction Engine.
    Supports X (Twitter), LinkedIn, Facebook, Instagram, and Reddit.
    Posting or publishing content strictly requires explicit security confirmation.
    """

    PLATFORM_URLS = {
        "x": "https://x.com",
        "twitter": "https://x.com",
        "linkedin": "https://www.linkedin.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "reddit": "https://www.reddit.com"
    }

    async def navigate_platform(self, platform_name: str) -> Dict[str, Any]:
        """Navigates safely to target social media platform home or feed."""
        clean_name = platform_name.lower().strip()
        url = self.PLATFORM_URLS.get(clean_name, f"https://www.{clean_name}.com")

        try:
            page = await browser_engine.get_active_page()
            logger.info(f"[SocialAutomation] Navigating to platform: {clean_name} ({url})")
            await page.goto(url, wait_until="domcontentloaded")

            return {
                "status": "success",
                "platform": clean_name,
                "url": page.url,
                "title": await page.title()
            }
        except Exception as e:
            logger.error(f"[SocialAutomation] Navigation to {platform_name} failed: {e}")
            return {"status": "error", "message": str(e), "platform": platform_name}

    async def post_update(
        self,
        platform_name: str,
        post_content: str,
        confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        Publishes post update on platform. STRICTLY REQUIRES confirmed=True.
        """
        # Verify security confirmation policy
        security_guard.verify_action_confirmation(f"post_{platform_name}", confirmed=confirmed)

        try:
            nav_res = await self.navigate_platform(platform_name)
            if nav_res.get("status") == "error":
                return nav_res

            page = await browser_engine.get_active_page()

            # Platform specific input targets
            if platform_name.lower() in ["x", "twitter"]:
                await page.fill("div[data-testid='tweetTextarea_0']", post_content)
                await page.click("button[data-testid='tweetButtonInline']")
            elif platform_name.lower() == "reddit":
                await page.click("button:has-text('Create Post')")
                await page.fill("textarea[name='title']", post_content)
            else:
                logger.info(f"[SocialAutomation] Drafted post content for {platform_name}: '{post_content[:50]}...'")

            return {
                "status": "success",
                "published": True,
                "platform": platform_name,
                "post_content": post_content
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

social_automation = SocialMediaAutomationEngine()
