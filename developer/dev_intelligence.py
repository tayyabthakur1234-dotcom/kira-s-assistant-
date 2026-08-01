"""
Developer Intelligence Engine Master Coordinator - KIRA AI OS (Phase 10)
Integrates code analysis, generation, debugging, testing, git/github operations,
docker, vscode, documentation, pair programming, and security scanning.
Connects with Phase 1-9 engines (Desktop, Vision, Browser, Voice, Memory, Plugins, UI, AI Router, Learning).
"""

from typing import Dict, Any, List, Optional
from utils.logger import logger
from developer.code_analyzer import code_analyzer
from developer.code_generator import code_generator
from developer.debugger import debugger
from developer.testing_engine import testing_engine
from developer.git_manager import git_manager
from developer.github_manager import github_manager
from developer.docker_manager import docker_manager
from developer.vscode_manager import vscode_manager
from developer.doc_generator import doc_generator
from developer.pair_programming import pair_programmer
from developer.security_scanner import security_scanner
from developer.project_manager import project_manager


class DeveloperIntelligenceEngine:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = workspace_root

    async def run_developer_task(
        self,
        task_type: str, # analyze, generate, debug, test, git_commit, github_repo, docker_build, project_create, pair_explain, security_scan
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main entry point for developer tasks across the system."""
        logger.info(f"DeveloperIntelligenceEngine executing task: {task_type}")

        if task_type == "code_analyze":
            return code_analyzer.analyze_codebase(payload.get("target_dir"))

        elif task_type == "code_generate":
            return await code_generator.generate_code(
                prompt=payload.get("prompt", ""),
                language=payload.get("language", "TypeScript"),
                component_type=payload.get("component_type", "file"),
                target_path=payload.get("target_path"),
                context_files=payload.get("context_files")
            )

        elif task_type == "code_debug":
            return await debugger.debug_project(
                command=payload.get("command"),
                stack_trace=payload.get("stack_trace"),
                file_context=payload.get("file_context"),
                auto_apply_fix=payload.get("auto_apply_fix", False)
            )

        elif task_type == "code_test":
            return await testing_engine.run_tests(
                test_type=payload.get("test_type", "unit"),
                test_path=payload.get("test_path")
            )

        elif task_type == "git_commit":
            return await git_manager.commit_changes(
                message=payload.get("message"),
                files=payload.get("files"),
                auto_generate_message=payload.get("auto_generate_message", True)
            )

        elif task_type == "github_repository":
            return await github_manager.create_repository(
                repo_name=payload.get("repo_name", "kira-project"),
                description=payload.get("description", "Created by KIRA Developer Intelligence"),
                private=payload.get("private", False)
            )

        elif task_type == "docker_build":
            return docker_manager.build_image(tag=payload.get("tag", "kira-app:latest"))

        elif task_type == "project_create":
            return await project_manager.create_project(
                project_name=payload.get("project_name", "New Kira App"),
                tech_stack=payload.get("tech_stack", "TypeScript / Python"),
                template=payload.get("template", "fullstack")
            )

        elif task_type == "pair_explain":
            return await pair_programmer.explain_code(
                code_snippet=payload.get("code_snippet", ""),
                language=payload.get("language", "TypeScript")
            )

        elif task_type == "security_scan":
            return security_scanner.scan_security()

        else:
            return {
                "status": "error",
                "message": f"Unknown task type '{task_type}'"
            }


dev_intelligence = DeveloperIntelligenceEngine()
