import urllib.parse
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from browser.engine import browser_engine
from utils.logger import logger

class GoogleSearchEngine:
    """
    Automated Google Search Engine for queries, result extraction, and top result navigation.
    """

    async def search(self, query: str) -> Dict[str, Any]:
        """Performs Google search and extracts result links and titles."""
        try:
            encoded_q = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_q}"

            page = await browser_engine.get_active_page()
            logger.info(f"[GoogleSearch] Searching Google for: '{query}'")
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

            # Extract search results via DOM & BeautifulSoup fallback
            content = await page.content()
            results = self._parse_google_html(content)

            return {
                "status": "success",
                "query": query,
                "search_url": search_url,
                "results_count": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"[GoogleSearch] Search failed: {e}")
            return {"status": "error", "message": str(e), "query": query}

    async def open_first_result(self, query: str) -> Dict[str, Any]:
        """Performs Google search and automatically navigates to the #1 organic search result."""
        search_res = await self.search(query)
        if search_res.get("status") == "error":
            return search_res

        results = search_res.get("results", [])
        if not results:
            return {"status": "error", "message": f"No organic search results found for query: '{query}'"}

        first_url = results[0]["url"]
        logger.info(f"[GoogleSearch] Opening first result: {first_url}")
        page = await browser_engine.get_active_page()
        response = await page.goto(first_url, wait_until="domcontentloaded", timeout=30000)

        return {
            "status": "success",
            "opened_result_title": results[0]["title"],
            "url": page.url,
            "page_title": await page.title(),
            "http_status": response.status if response else 200
        }

    async def open_selected_result(self, index: int) -> Dict[str, Any]:
        """Opens result at specified index from current active Google search page."""
        try:
            page = await browser_engine.get_active_page()
            content = await page.content()
            results = self._parse_google_html(content)

            if not results or index < 0 or index >= len(results):
                return {"status": "error", "message": f"Invalid result index {index}. Found {len(results)} results."}

            target = results[index]
            await page.goto(target["url"], wait_until="domcontentloaded", timeout=30000)

            return {
                "status": "success",
                "opened_title": target["title"],
                "url": page.url,
                "page_title": await page.title()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _parse_google_html(self, html: str) -> List[Dict[str, str]]:
        """Parses Google Search result HTML using BeautifulSoup."""
        soup = BeautifulSoup(html, "lxml")
        results = []

        # Find main search result containers
        for g in soup.find_all('div', class_='g'):
            anchor = g.find('a', href=True)
            h3 = g.find('h3')
            snippet_div = g.find('div', class_=lambda c: c and 'VwiC3b' in c) or g.find('div', class_='IsZAfe')

            if anchor and h3 and anchor['href'].startswith('http'):
                url = anchor['href']
                title = h3.get_text().strip()
                snippet = snippet_div.get_text().strip() if snippet_div else ""
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })

        # Fallback general link query if class names changed
        if not results:
            for a in soup.find_all('a', href=True):
                href = a['href']
                h3 = a.find('h3')
                if h3 and href.startswith('http') and 'google.com' not in href:
                    results.append({
                        "title": h3.get_text().strip(),
                        "url": href,
                        "snippet": ""
                    })

        return results

google_search_engine = GoogleSearchEngine()
