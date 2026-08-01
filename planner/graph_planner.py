import uuid
import json
import os
import aiohttp
from typing import Dict, Any, List, Optional
from config.settings import settings
from utils.logger import logger

try:
    import networkx as nx
except ImportError:
    nx = None


class GraphPlanner:
    """
    Autonomous DAG Graph Planner for KIRA AI OS Phase 5.
    Breaks down complex high-level user goals into structured, ordered sub-tasks
    with explicit dependency mapping, retries, and fallback strategies.
    """

    def __init__(self):
        self.max_retries = settings.max_planner_retries

    async def decompose_goal(self, goal_prompt: str) -> Dict[str, Any]:
        """
        Decomposes a complex goal (e.g. 'Build a React website' or 'Install VS Code and Python')
        into an ordered list of tasks with dependencies and execution engines.
        """
        plan_id = f"plan_{uuid.uuid4().hex[:10]}"
        logger.info(f"[GraphPlanner] Decomposing goal: '{goal_prompt}' (plan_id={plan_id})")

        # Query Gemini API or generate structured heuristic DAG tasks
        tasks = await self._generate_task_dag(goal_prompt)

        # Build NetworkX dependency graph if available
        dep_graph = {}
        if nx:
            G = nx.DiGraph()
            for t in tasks:
                G.add_node(t["id"], task=t)
                for dep in t.get("dependencies", []):
                    G.add_edge(dep, t["id"])

            is_dag = nx.is_directed_acyclic_graph(G)
            dep_graph = {
                "is_dag": is_dag,
                "node_count": G.number_of_nodes(),
                "edge_count": G.number_of_edges()
            }

        return {
            "status": "success",
            "plan_id": plan_id,
            "goal": goal_prompt,
            "task_count": len(tasks),
            "tasks": tasks,
            "graph_metadata": dep_graph
        }

    async def _generate_task_dag(self, goal_prompt: str) -> List[Dict[str, Any]]:
        """Generates DAG task nodes with dependency pointers."""
        lower = goal_prompt.lower()

        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")

        # 1. Gemini API Structured Decomposition if key is available
        if api_key and api_key != "MY_GEMINI_API_KEY":
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                prompt = (
                    "Break down the following goal into a JSON list of sequential atomic sub-tasks for an AI OS agent. "
                    "Each task MUST have fields: id (str e.g. 'task_1'), title (str), description (str), "
                    "engine (str: 'desktop', 'browser', 'vision', 'voice', or 'system'), dependencies (list of str task ids). "
                    f"Goal: '{goal_prompt}'\n"
                    "Respond strictly with valid JSON list."
                )
                payload = {"contents": [{"parts": [{"text": prompt}]}]}

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=8.0) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                            clean_json = raw_text.replace("```json", "").replace("```", "").strip()
                            parsed_tasks = json.loads(clean_json)
                            if isinstance(parsed_tasks, list) and len(parsed_tasks) > 0:
                                return parsed_tasks
            except Exception as ex:
                logger.warning(f"[GraphPlanner] Gemini decomposition fallback: {ex}")

        # 2. Production Heuristic Task Graph Templates for Autonomous Goals

        # Pattern A: Install software tools (e.g. VS Code, Python)
        if "install" in lower:
            return [
                {
                    "id": "task_1",
                    "title": "Detect OS & Download Installers",
                    "description": f"Identify system OS and download binaries for '{goal_prompt}' via Browser Engine.",
                    "engine": "browser",
                    "dependencies": []
                },
                {
                    "id": "task_2",
                    "title": "Execute System Installer",
                    "description": "Run installer package with administrative privilege check.",
                    "engine": "desktop",
                    "dependencies": ["task_1"]
                },
                {
                    "id": "task_3",
                    "title": "Verify Installation & Environment",
                    "description": "Verify executable presence in PATH and speak status update.",
                    "engine": "voice",
                    "dependencies": ["task_2"]
                }
            ]

        # Pattern B: Create Project (e.g. AI project, React app)
        if "create" in lower or "build" in lower or "project" in lower:
            return [
                {
                    "id": "task_1",
                    "title": "Create Project Directory Structure",
                    "description": "Initialize file directory and workspace folders.",
                    "engine": "desktop",
                    "dependencies": []
                },
                {
                    "id": "task_2",
                    "title": "Initialize Git & Virtual Environment",
                    "description": "Run git init and configure project environment.",
                    "engine": "desktop",
                    "dependencies": ["task_1"]
                },
                {
                    "id": "task_3",
                    "title": "Generate Boilerplate & README",
                    "description": "Create standard configuration files and documentation.",
                    "engine": "desktop",
                    "dependencies": ["task_2"]
                },
                {
                    "id": "task_4",
                    "title": "Open Workspace in Code Editor",
                    "description": "Launch VS Code or IDE targeting created project folder.",
                    "engine": "desktop",
                    "dependencies": ["task_3"]
                }
            ]

        # Pattern C: Default Generic Goal Breakdown
        return [
            {
                "id": "task_1",
                "title": "Analyze Goal & Screen Context",
                "description": "Inspect active screen and system state using Vision Engine.",
                "engine": "vision",
                "dependencies": []
            },
            {
                "id": "task_2",
                "title": "Execute Primary Action Sequence",
                "description": f"Perform actions to achieve: '{goal_prompt}'.",
                "engine": "desktop",
                "dependencies": ["task_1"]
            },
            {
                "id": "task_3",
                "title": "Verify Results & Speak Summary",
                "description": "Evaluate final state and provide voice summary.",
                "engine": "voice",
                "dependencies": ["task_2"]
            }
        ]

graph_planner = GraphPlanner()
