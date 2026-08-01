import unittest
from fastapi.testclient import TestClient
from api.main import app
from router.model_router import model_router, REQ_CODING, REQ_VISION, REQ_REASONING, REQ_DESKTOP_CONTROL, MODEL_GROK_4, MODEL_GEMINI_25_PRO
from agents.multi_agent_system import multi_agent_system, SecurityAgent, PlannerAgent, SelfVerificationEngine

client = TestClient(app)

class TestRouterAndMultiAgentSystem(unittest.IsolatedAsyncioTestCase):

    def test_model_router_classification(self):
        cat_code = model_router.classify_request("Write a Python script to parse JSON logs")
        assert cat_code == REQ_CODING

        cat_vis = model_router.classify_request("Analyze this screenshot image", has_image=True)
        assert cat_vis == REQ_VISION

        cat_math = model_router.classify_request("Solve calculus equation integral x^2 dx")
        assert cat_math == "math"

        cat_desktop = model_router.classify_request("Click on Chrome window and open app")
        assert cat_desktop == REQ_DESKTOP_CONTROL

    def test_model_selection_and_override(self):
        candidates = model_router.select_model(REQ_CODING)
        assert candidates[0] == MODEL_GROK_4

        # Override preference
        model_router.user_overrides[REQ_CODING] = MODEL_GEMINI_25_PRO
        overridden = model_router.select_model(REQ_CODING)
        assert overridden[0] == MODEL_GEMINI_25_PRO
        # Reset override
        del model_router.user_overrides[REQ_CODING]

    async def test_model_failover_execution(self):
        res = await model_router.execute_with_failover(
            prompt="Refactor API endpoint",
            category=REQ_CODING
        )
        assert res["status"] == "success"
        assert "model_used" in res
        assert len(res["attempts"]) >= 1

    async def test_security_agent_danger_detection(self):
        sec_agent = SecurityAgent()
        safe_res = await sec_agent.inspect_and_validate("Show active system metrics")
        assert safe_res["safe"] is True

        danger_res = await sec_agent.inspect_and_validate("Execute dangerous command: rm -rf /")
        assert danger_res["safe"] is False
        assert danger_res["requires_confirmation"] is True

    async def test_self_verification_engine(self):
        verifier = SelfVerificationEngine()
        pass_res = await verifier.verify_result("Build feature", {"status": "success", "result": "Done"})
        assert pass_res["verified"] is True
        assert pass_res["confidence_score"] > 0.9

        fail_res = await verifier.verify_result("Build feature", {"status": "failed", "error": "Syntax error"})
        assert fail_res["verified"] is False

    async def test_multi_agent_workflow_orchestration(self):
        workflow = await multi_agent_system.execute_multi_agent_workflow("Create a clean dashboard feature")
        assert workflow["status"] == "success"
        assert workflow["total_agents_involved"] >= 3
        assert len(workflow["workflow_steps"]) >= 3

    # FastAPI Endpoints Tests
    def test_api_route_model(self):
        response = client.post("/router/model", json={"prompt": "Write a TypeScript function"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["category"] == REQ_CODING
        assert "recommended_primary_model" in data

    def test_api_route_task_execution(self):
        response = client.post("/router/task", json={"prompt": "Explain Quantum Computing"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_api_models_status(self):
        response = client.get("/models/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_supported_models"] >= 10

    def test_api_agents_list(self):
        response = client.get("/agents/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_agents"] == 10

    def test_api_agents_run_workflow(self):
        response = client.post("/agents/run", json={"goal": "Develop full-stack web scraping pipeline"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "workflow_steps" in data

    def test_api_agents_status(self):
        response = client.get("/agents/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"

if __name__ == "__main__":
    unittest.main()
