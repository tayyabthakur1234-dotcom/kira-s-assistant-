from typing import Dict, Any, List, Optional
from browser.engine import browser_engine
from utils.security import security_guard
from utils.logger import logger

class GmailAutomationEngine:
    """
    Gmail & Web Mail Automation Engine.
    Handles inbox browsing, email search, composition, file attachments, and security-confirmed sending.
    """

    async def open_gmail() -> Dict[str, Any]:
        pass

    async def open_inbox(self) -> Dict[str, Any]:
        """Navigates to Gmail inbox interface."""
        try:
            page = await browser_engine.get_active_page()
            await page.goto("https://mail.google.com/", wait_until="domcontentloaded")
            return {
                "status": "success",
                "url": page.url,
                "title": await page.title()
            }
        except Exception as e:
            logger.error(f"[GmailAutomation] Failed opening Gmail: {e}")
            return {"status": "error", "message": str(e)}

    async def search_mail(self, query: str) -> Dict[str, Any]:
        """Searches emails in Gmail search bar."""
        try:
            page = await browser_engine.get_active_page()
            if "mail.google.com" not in page.url:
                await self.open_inbox()

            # Fill search box
            search_input = "input[aria-label='Search mail']"
            await page.fill(search_input, query)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(2000)

            return {
                "status": "success",
                "query": query,
                "current_url": page.url
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def compose_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        attachment_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Composes email draft in Gmail with optional attachment."""
        try:
            page = await browser_engine.get_active_page()
            if "mail.google.com" not in page.url:
                await self.open_inbox()

            # Click Compose
            await page.click("div[role='button']:has-text('Compose')", timeout=10000)
            await page.wait_for_timeout(1000)

            # Fill recipient, subject, body
            await page.fill("input[aria-label='To']", recipient)
            await page.fill("input[name='subjectbox']", subject)
            await page.fill("div[aria-label='Message Body']", body)

            if attachment_path:
                try:
                    await page.set_input_files("input[type='file']", attachment_path)
                except Exception as att_err:
                    logger.warning(f"[GmailAutomation] Attachment failed: {att_err}")

            return {
                "status": "draft_created",
                "recipient": recipient,
                "subject": subject,
                "attachment": attachment_path,
                "ready_to_send": True
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        Sends email. STRICTLY REQUIRES confirmed=True (Security Confirmation Policy).
        """
        # Security Guard check
        security_guard.verify_action_confirmation("send_email", confirmed=confirmed)

        try:
            page = await browser_engine.get_active_page()

            # Compose draft first
            compose_res = await self.compose_email(recipient, subject, body)
            if compose_res.get("status") == "error":
                return compose_res

            # Click Send button
            await page.click("div[role='button']:has-text('Send')", timeout=5000)
            await page.wait_for_timeout(2000)

            return {
                "status": "success",
                "sent": True,
                "recipient": recipient,
                "subject": subject
            }
        except Exception as e:
            logger.error(f"[GmailAutomation] Send email failed: {e}")
            return {"status": "error", "message": str(e)}

gmail_automation = GmailAutomationEngine()
