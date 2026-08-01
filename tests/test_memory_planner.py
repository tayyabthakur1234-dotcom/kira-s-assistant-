import unittest
import asyncio
from fastapi.testclient import TestClient
from api.main import app
from memory.sqlite_store import sqlite_memory_store
from memory.vector_store import vector_memory_store
from memory.memory_manager import memory_manager
from planner.graph_planner import graph_planner
from planner.task_manager import task_manager
from planner.reflection import reflection_engine
from planner.agent_executor import agent_executor

client = TestClient(app)


class TestMemoryPlannerEngine(unittest.IsolatedAsyncioTestCase):

    def test_sqlite_memory_store(self):
        assert sqlite_memory_store.set_user_preference("coding_style", "pep8", "coding") is True
        assert sqlite_memory_store.get_user_preference("coding_style") == "pep8"

        profile = sqlite_memory_store.get_all_user_profile()
        assert "coding_style" in profile

        m_id = "test_mem_001"
        assert sqlite_memory_store.insert_memory(
            memory_id=m_id,
            memory_type="preference",
            category="coding",
            content="User prefers Python 3.12 and FastAPI.",
            importance_score=0.9
        ) is True

        mem = sqlite_memory_store.get_memory(m_id)
        assert mem is not None
        assert mem["content"] == "User prefers Python 3.12 and FastAPI."

        mems = sqlite_memory_store.list_memories(memory_type="preference")
        assert len(mems) > 0

        assert sqlite_memory_store.delete_memory(m_id) is True

    def test_vector_memory_store(self):
        m_id = "test_vec_001"
        text = "KIRA AI uses SQLite and ChromaDB for long-term memory."
        assert vector_memory_store.add_memory_vector(
            memory_id=m_id,
            text_content=text,
            metadata={"category": "ai_tech"}
        ) is True

        hits = vector_memory_store.semantic_search("ChromaDB long-term memory", top_k=3)
        assert len(hits) > 0

        assert vector_memory_store.delete_vector(m_id) is True

    def test_memory_manager_unified(self):
        memory_manager.update_working_memory("active_window", "VS Code")
        assert memory_manager.get_working_memory("active_window") == "VS Code"

        res_store = memory_manager.store_memory(
            content="I always use Gemini API for primary reasoning.",
            memory_type="preference",
            category="ai_models",
            importance_score=0.8
        )
        assert res_store["status"] == "success"
        mem_id = res_store["memory_id"]

        res_search = memory_manager.search_memories(query="Gemini API primary reasoning", limit=5)
        assert res_search["status"] == "success"
        assert res_search["results_count"] > 0

        memory_manager.auto_extract_from_text("I prefer dark mode in all IDEs.")
        pref_search = memory_manager.search_memories(query="dark mode")
        assert pref_search["results_count"] > 0

        assert memory_manager.delete_memory(mem_id) is True

    async def test_graph_planner(self):
        decomp = await graph_planner.decompose_goal("Install VS Code and Python")
        assert decomp["status"] == "success"
        assert "plan_id" in decomp
        assert len(decomp["tasks"]) >= 2

    def test_task_manager(self):
        tasks = [
            {"id": "t1", "title": "Download installer", "engine": "browser", "dependencies": []},
            {"id": "t2", "title": "Run installer", "engine": "desktop", "dependencies": ["t1"]}
        ]
        plan_record = task_manager.register_plan("plan_test_001", "Install tool", tasks)
        assert plan_record["plan_id"] == "plan_test_001"

        status = task_manager.get_plan_status("plan_test_001")
        assert status["plan_id"] == "plan_test_001"
        assert status["total_tasks"] == 2

        action_res = task_manager.perform_action("plan_test_001", "pause")
        assert action_res["status"] == "success"
        assert action_res["new_status"] == "paused"

        action_res2 = task_manager.perform_action("plan_test_001", "resume")
        assert action_res2["status"] == "success"

    def test_self_reflection_engine(self):
        res = reflection_engine.evaluate_task_execution(
            task_id="t1",
            goal="Open VS Code",
            execution_output={"status": "success", "engine": "desktop"}
        )
        assert res["status"] == "success"
        assert res["is_success"] is True
        assert "lesson_id" in res

    async def test_agent_executor(self):
        tasks = [
            {"id": "t1", "title": "Inspect screen", "engine": "vision", "description": "Check monitor", "dependencies": []},
            {"id": "t2", "title": "Speak status", "engine": "voice", "description": "Speak summary", "dependencies": ["t1"]}
        ]
        task_manager.register_plan("plan_exec_001", "Inspect and speak", tasks)

        exec_res = await agent_executor.execute_plan("plan_exec_001")
        assert exec_res["status"] == "success"
        assert "plan_status" in exec_res

    def test_phase5_memory_api_endpoints(self):
        resp_store = client.post("/memory/store", json={
            "content": "KIRA AI Phase 5 memory test entry.",
            "memory_type": "semantic",
            "category": "unit_test",
            "importance_score": 0.75
        })
        assert resp_store.status_code == 200
        data_store = resp_store.json()
        assert data_store["status"] == "success"
        mem_id = data_store["data"]["memory_id"]

        resp_search = client.post("/memory/search", json={
            "query": "KIRA AI Phase 5 memory test",
            "limit": 5
        })
        assert resp_search.status_code == 200
        assert resp_search.json()["status"] == "success"

        resp_update = client.post("/memory/update", json={
            "memory_id": mem_id,
            "new_content": "Updated KIRA AI Phase 5 memory entry."
        })
        assert resp_update.status_code == 200

        resp_export = client.post("/memory/export")
        assert resp_export.status_code == 200

        resp_del = client.post("/memory/delete", json={"memory_id": mem_id})
        assert resp_del.status_code == 200

    def test_phase5_planner_api_endpoints(self):
        resp_create = client.post("/planner/create", json={
            "goal": "Create a new AI project"
        })
        assert resp_create.status_code == 200
        data_create = resp_create.json()
        assert data_create["status"] == "success"
        plan_id = data_create["data"]["plan_id"]

        resp_status = client.post("/planner/status", json={"plan_id": plan_id})
        assert resp_status.status_code == 200

        resp_tasks = client.post("/tasks/list")
        assert resp_tasks.status_code == 200

        resp_action = client.post("/tasks/action", json={
            "target_id": plan_id,
            "action": "pause"
        })
        assert resp_action.status_code == 200

        resp_run = client.post("/planner/run", json={"plan_id": plan_id})
        assert resp_run.status_code == 200


if __name__ == "__main__":
    unittest.main()
