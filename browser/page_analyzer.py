import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from browser.engine import browser_engine
from utils.logger import logger

class PageAnalyzer:
    """
    DOM & BeautifulSoup Page Analyzer and Content Extractor Engine.
    Understands webpage layout, extracts text, headings, links, buttons, forms, tables,
    detects login forms, CAPTCHA challenges, and converts page content to Markdown or HTML.
    """

    async def analyze_page(self) -> Dict[str, Any]:
        """Performs full structural analysis of active browser page."""
        try:
            page = await browser_engine.get_active_page()
            url = page.url
            title = await page.title()
            content_html = await page.content()

            soup = BeautifulSoup(content_html, "lxml")

            # Extract headings
            headings = []
            for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                headings.append({
                    "level": tag.name,
                    "text": tag.get_text().strip()
                })

            # Extract links
            links = []
            for a in soup.find_all('a', href=True):
                text = a.get_text().strip()
                href = a['href']
                if text and href:
                    links.append({"text": text, "href": href})

            # Extract buttons
            buttons = []
            for b in soup.find_all(['button', 'input']):
                btn_text = b.get_text().strip() or b.get('value', '') or b.get('aria-label', '')
                if btn_text:
                    buttons.append({"text": btn_text, "type": b.get('type', 'button')})

            # Extract forms
            forms = []
            for f in soup.find_all('form'):
                inputs = [{"name": i.get('name'), "type": i.get('type', 'text')} for i in f.find_all('input')]
                forms.append({
                    "action": f.get('action'),
                    "method": f.get('method', 'get'),
                    "inputs": inputs
                })

            # Extract tables
            tables_data = self._extract_tables_soup(soup)

            # Detect Login & CAPTCHA
            is_login_page = self._detect_login_form(soup, forms)
            is_captcha_present = self._detect_captcha(soup)

            return {
                "url": url,
                "title": title,
                "headings_count": len(headings),
                "headings": headings[:20],
                "links_count": len(links),
                "links_sample": links[:15],
                "buttons_count": len(buttons),
                "buttons": buttons[:15],
                "forms_count": len(forms),
                "forms": forms,
                "tables_count": len(tables_data),
                "tables": tables_data,
                "is_login_page": is_login_page,
                "is_captcha_present": is_captcha_present
            }
        except Exception as e:
            logger.error(f"[PageAnalyzer] Page analysis failed: {e}")
            return {"status": "error", "message": str(e)}

    async def extract_text(self) -> Dict[str, Any]:
        """Extracts clean visible plain text from active webpage."""
        try:
            page = await browser_engine.get_active_page()
            text = await page.evaluate("() => document.body.innerText")
            clean_text = re.sub(r'\n+', '\n', text).strip()
            return {
                "status": "success",
                "url": page.url,
                "text_length": len(clean_text),
                "text": clean_text
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def export_markdown(self) -> Dict[str, Any]:
        """Converts active webpage content into structured Markdown format."""
        try:
            page = await browser_engine.get_active_page()
            html = await page.content()
            soup = BeautifulSoup(html, "lxml")

            # Remove scripts, styles, navs, footers
            for elem in soup(["script", "style", "nav", "footer", "header", "svg"]):
                elem.decompose()

            lines = []
            title = await page.title()
            lines.append(f"# {title}\n")

            for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'pre']):
                if tag.name.startswith('h'):
                    level = int(tag.name[1])
                    lines.append(f"{'#' * level} {tag.get_text().strip()}\n")
                elif tag.name == 'p':
                    lines.append(f"{tag.get_text().strip()}\n")
                elif tag.name in ['ul', 'ol']:
                    for li in tag.find_all('li'):
                        lines.append(f"- {li.get_text().strip()}")
                    lines.append("")
                elif tag.name == 'pre':
                    lines.append(f"```\n{tag.get_text().strip()}\n```\n")

            markdown_content = "\n".join(lines)

            return {
                "status": "success",
                "url": page.url,
                "title": title,
                "markdown": markdown_content
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _extract_tables_soup(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """Extracts structured table matrices from page."""
        tables = []
        for table in soup.find_all('table'):
            table_rows = []
            for tr in table.find_all('tr'):
                row_cells = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
                if row_cells:
                    table_rows.append(row_cells)
            if table_rows:
                tables.append(table_rows)
        return tables

    def _detect_login_form(self, soup: BeautifulSoup, forms: List[Dict[str, Any]]) -> bool:
        """Detects if page is a login/authentication interface."""
        page_text = soup.get_text().lower()
        if "login" in page_text or "sign in" in page_text or "password" in page_text:
            for f in forms:
                types = [i.get("type") for i in f.get("inputs", [])]
                if "password" in types:
                    return True
        return False

    def _detect_captcha(self, soup: BeautifulSoup) -> bool:
        """Detects presence of reCAPTCHA, hCaptcha, Cloudflare turnstile, or puzzle elements."""
        html_str = str(soup).lower()
        captcha_keywords = ["recaptcha", "hcaptcha", "cf-turnstile", "g-recaptcha", "captcha", "cf-challenge"]
        return any(kw in html_str for kw in captcha_keywords)

page_analyzer = PageAnalyzer()
