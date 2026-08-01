"""
Project Manager Module - KIRA AI Operating System (Phase 10)
Handles end-to-end project lifecycles: creates new project scaffolding, opens and analyzes existing projects,
refactors architectures, generates folder structures, requirements, READMEs, documentation, and changelogs.
"""

import os
import json
from typing import Dict, Any, List, Optional
from utils.logger import logger
from developer.code_analyzer import code_analyzer
from developer.doc_generator import doc_generator


class ProjectManager:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)

    async def create_project(
        self,
        project_name: str,
        tech_stack: str = "TypeScript / React / Express / Python",
        template: str = "fullstack",
        target_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates complete scaffolding for a new software project."""
        base_dir = os.path.abspath(target_dir or os.path.join(self.workspace_root, "projects", project_name.lower().replace(" ", "-")))
        os.makedirs(base_dir, exist_ok=True)

        # Standard folder structure creation
        folders = ["src", "src/components", "src/services", "api", "api/routers", "tests", "public", "config"]
        for f in folders:
            os.makedirs(os.path.join(base_dir, f), exist_ok=True)

        # Generate README & Docs
        readme_res = await doc_generator.generate_readme(project_name)
        changelog_res = await doc_generator.generate_changelog()

        # Generate requirements.txt
        req_content = """fastapi>=0.110.0
uvicorn>=0.28.0
pydantic>=2.6.0
google-genai>=2.0.0
pytest>=8.0.0
requests>=2.31.0
python-dotenv>=1.0.0
"""
        with open(os.path.join(base_dir, "requirements.txt"), 'w', encoding='utf-8') as f:
            f.write(req_content)

        # Generate package.json
        pkg_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "dev": "tsx server.ts",
                "build": "vite build && esbuild server.ts --bundle --platform=node --format=cjs --outfile=dist/server.cjs",
                "start": "node dist/server.cjs"
            },
            "dependencies": {
                "express": "^4.19.0",
                "react": "^19.0.0",
                "react-dom": "^19.0.0",
                "lucide-react": "^0.350.0",
                "motion": "^12.0.0"
            }
        }
        with open(os.path.join(base_dir, "package.json"), 'w', encoding='utf-8') as f:
            json.dump(pkg_json, f, indent=2)

        return {
            "status": "success",
            "project_name": project_name,
            "project_path": base_dir,
            "template": template,
            "tech_stack": tech_stack,
            "folders_created": folders,
            "manifests": ["package.json", "requirements.txt", "README.md", "CHANGELOG.md"]
        }

    def analyze_project(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """Analyzes project architecture and metrics."""
        return code_analyzer.analyze_codebase(target_dir or self.workspace_root)


project_manager = ProjectManager()
