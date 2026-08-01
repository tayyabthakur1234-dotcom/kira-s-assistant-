import unittest
from bs4 import BeautifulSoup
from browser.navigation import navigation_manager
from browser.search import google_search_engine
from browser.page_analyzer import page_analyzer
from browser.gmail_automation import gmail_automation
from browser.social_automation import social_automation
from utils.security import SecurityException

class TestBrowserEngine(unittest.IsolatedAsyncioTestCase):

    def test_navigation_manager_bookmarks_and_history(self):
        navigation_manager.add_bookmark("GitHub", "https://github.com")
        bookmarks = navigation_manager.get_bookmarks()
        assert len(bookmarks) > 0
        assert bookmarks[-1]["title"] == "GitHub"

    def test_google_search_html_parsing(self):
        html = """
        <html>
            <body>
                <div class="g">
                    <a href="https://github.com/open-interpreter"><h3 class="LC22ld">Open Interpreter GitHub</h3></a>
                    <div class="VwiC3b">Open-source code interpreter for LLMs.</div>
                </div>
            </body>
        </html>
        """
        results = google_search_engine._parse_google_html(html)
        assert len(results) == 1
        assert results[0]["title"] == "Open Interpreter GitHub"
        assert "github.com" in results[0]["url"]

    def test_page_analyzer_login_and_captcha_detection(self):
        html_login = """
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="text" name="username" />
                    <input type="password" name="password" />
                    <input type="submit" value="Sign In" />
                </form>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_login, "lxml")
        forms = [{"inputs": [{"type": "text"}, {"type": "password"}]}]
        is_login = page_analyzer._detect_login_form(soup, forms)
        assert is_login is True

        html_captcha = "<div>Please complete the reCAPTCHA challenge below.</div>"
        soup_captcha = BeautifulSoup(html_captcha, "lxml")
        is_captcha = page_analyzer._detect_captcha(soup_captcha)
        assert is_captcha is True

    async def test_gmail_send_email_security_guard(self):
        with self.assertRaises(SecurityException):
            await gmail_automation.send_email(
                recipient="test@example.com",
                subject="Test Subject",
                body="Test Body",
                confirmed=False
            )

    async def test_social_post_security_guard(self):
        with self.assertRaises(SecurityException):
            await social_automation.post_update(
                platform_name="x",
                post_content="Automated Tweet",
                confirmed=False
            )

if __name__ == "__main__":
    unittest.main()
