import subprocess
import os
from typing import Dict, Any, Optional, List
from browser.engine import browser_engine
from utils.logger import logger

class GitHubAutomationEngine:
    """
    Automated GitHub Web & Git CLI Automation Engine.
    Handles login, cloning, repository creation, issue management, PR inspection, downloading zip, and git commits/pushes.
    """

    async def login(self, username: str, password_or_token: str) -> Dict[str, Any]:
        """Logs into GitHub using Web UI."""
        try:
            page = await browser_engine.get_active_page()
            await page.goto("https://github.com/login", wait_until="domcontentloaded")

            await page.fill("input[name='login']", username)
            await page.fill("input[name='password']", password_or_token)
            await page.click("input[type='submit']")

            await page.wait_for_load_state("domcontentloaded")
            is_logged_in = "login" not in page.url

            return {
                "status": "success" if is_logged_in else "failed",
                "logged_in": is_logged_in,
                "current_url": page.url
            }
        except Exception as e:
            logger.error(f"[GitHubAutomation] Login failed: {e}")
            return {"status": "error", "message": str(e)}

    async def create_repository(
        self,
        repo_name: str,
        description: str = "",
        private: bool = False
    ) -> Dict[str, Any]:
        """Creates a new repository on GitHub via web interface."""
        try:
            page = await browser_engine.get_active_page()
            await page.goto("https://github.com/new", wait_until="domcontentloaded")

            # Fill repo name
            await page.fill("input[data-testid='repository-name-input']", repo_name)
            await page.wait_for_timeout(1000)

            # Optional description
            if description:
                try:
                    await page.fill("input[id=':r4:']", description)
                except Exception:
                    pass

            if private:
                try:
                    await page.click("input[value='private']")
                except Exception:
                    pass

            # Click create
            await page.click("button:has-text('Create repository')")
            await page.wait_for_load_state("domcontentloaded")

            return {
                "status": "success",
                "repo_name": repo_name,
                "repo_url": page.url,
                "created": True
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def clone_repository(self, repo_url: str, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """Clones a Git repository locally using Git CLI."""
        try:
            cmd = ["git", "clone", repo_url]
            if target_dir:
                cmd.append(target_dir)

            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {
                "status": "success",
                "command": " ".join(cmd),
                "output": res.stdout,
                "cloned_repo": repo_url
            }
        except Exception as e:
            logger.error(f"[GitHubAutomation] Clone failed: {e}")
            return {"status": "error", "message": str(e)}

    async def create_issue(self, repo_owner_name: str, title: str, body: str) -> Dict[str, Any]:
        """Creates an issue in target repository (owner/repo)."""
        try:
            page = await browser_engine.get_active_page()
            issue_url = f"https://github.com/{repo_owner_name}/issues/new"
            await page.goto(issue_url, wait_until="domcontentloaded")

            await page.fill("input[name='issue[title]']", title)
            await page.fill("textarea[name='issue[body]']", body)
            await page.click("button:has-text('Submit new issue')")

            await page.wait_for_load_state("domcontentloaded")
            return {
                "status": "success",
                "issue_title": title,
                "issue_url": page.url
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def read_pull_requests(self, repo_owner_name: str) -> Dict[str, Any]:
        """Extracts list of open Pull Requests from GitHub repository."""
        try:
            page = await browser_engine.get_active_page()
            pr_url = f"https://github.com/{repo_owner_name}/pulls"
            await page.goto(pr_url, wait_until="domcontentloaded")

            pr_elements = await page.query_selector_all("a[id^='issue_']")
            prs = []
            for pr in pr_elements[:10]:
                text = await pr.inner_text()
                href = await pr.get_attribute("href")
                prs.append({"title": text.strip(), "url": f"https://github.com{href}"})

            return {
                "status": "success",
                "repo": repo_owner_name,
                "prs_count": len(prs),
                "pull_requests": prs
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

github_automation = GitHubAutomationEngine()
