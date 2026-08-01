import os
from typing import Dict, Any, List, Optional
from browser.engine import browser_engine
from config.settings import settings
from utils.logger import logger

class FormFillingEngine:
    """
    Automated Web Form Filling, Uploads, Downloads, and Verification Engine.
    """

    async def fill_form(
        self,
        field_values: Dict[str, str], # { "selector_or_placeholder_or_label": "value" }
        submit_selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fills multiple input fields and optionally submits form."""
        try:
            page = await browser_engine.get_active_page()
            filled_fields = []

            for target, value in field_values.items():
                selector = self._resolve_field_selector(target)
                try:
                    await page.fill(selector, value, timeout=5000)
                    filled_fields.append({"target": target, "selector": selector, "status": "filled"})
                except Exception as ex:
                    # Retry using placeholder or text locator
                    try:
                        await page.get_by_placeholder(target).fill(value, timeout=3000)
                        filled_fields.append({"target": target, "method": "placeholder", "status": "filled"})
                    except Exception:
                        filled_fields.append({"target": target, "error": str(ex), "status": "failed"})

            submitted = False
            if submit_selector:
                try:
                    await page.click(submit_selector, timeout=5000)
                    await page.wait_for_load_state("domcontentloaded", timeout=10000)
                    submitted = True
                except Exception as ex:
                    logger.warning(f"[FormFilling] Submit click failed: {ex}")

            return {
                "status": "success",
                "filled_fields": filled_fields,
                "form_submitted": submitted,
                "current_url": page.url
            }
        except Exception as e:
            logger.error(f"[FormFilling] Form fill operation failed: {e}")
            return {"status": "error", "message": str(e)}

    async def upload_file(self, selector: str, file_path: str) -> Dict[str, Any]:
        """Uploads file to file input control."""
        try:
            if not os.path.exists(file_path):
                return {"status": "error", "message": f"Local file not found at path: {file_path}"}

            page = await browser_engine.get_active_page()
            await page.set_input_files(selector, file_path, timeout=10000)

            return {
                "status": "success",
                "selector": selector,
                "uploaded_file": file_path
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def download_file_click(self, download_trigger_selector: str, custom_filename: Optional[str] = None) -> Dict[str, Any]:
        """Triggers file download click and saves file to configured downloads directory."""
        try:
            page = await browser_engine.get_active_page()
            os.makedirs(settings.browser_downloads_dir, exist_ok=True)

            async with page.expect_download(timeout=30000) as download_info:
                await page.click(download_trigger_selector, timeout=10000)

            download = await download_info.value
            save_name = custom_filename or download.suggested_filename
            destination_path = os.path.join(settings.browser_downloads_dir, save_name)
            await download.save_as(destination_path)

            return {
                "status": "success",
                "original_filename": download.suggested_filename,
                "saved_path": destination_path,
                "file_size_bytes": os.path.getsize(destination_path) if os.path.exists(destination_path) else 0
            }
        except Exception as e:
            logger.error(f"[FormFilling] Download click failed: {e}")
            return {"status": "error", "message": str(e)}

    def _resolve_field_selector(self, target: str) -> str:
        """Converts raw name/id/placeholder hint into valid CSS selector if needed."""
        if target.startswith('#') or target.startswith('.') or target.startswith('[') or '//' in target:
            return target
        return f"input[name='{target}'], input[id='{target}'], textarea[name='{target}']"

form_filling_engine = FormFillingEngine()
