import unittest
from fastapi.testclient import TestClient
from api.main import app
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

client = TestClient(app)

class TestDeveloperIntelligenceEngine(unittest.IsolatedAsyncioTestCase):

    def test_code_analyzer(self):
        report = code_analyzer.analyze_codebase(".")
        assert report["status"] == "success"
        assert "architecture" in report
        assert "complexity_health_score" in report

    async def test_code_generator(self):
        res = await code_generator.generate_code(
            prompt="Create a helper function to validate emails",
            language="TypeScript"
        )
        assert res["status"] == "success"
        assert res["language"] == "TypeScript"
        assert "artifact" in res

    async def test_debugger(self):
        res = await debugger.debug_project(
            stack_trace="TypeError: Cannot read property 'map' of undefined at line 42"
        )
        assert res["status"] == "error_analyzed"
        assert "root_cause_summary" in res

    async def test_testing_engine(self):
        res = await testing_engine.run_tests(test_type="unit")
        assert res["status"] == "completed"
        assert "test_suites" in res

    def test_git_manager_status(self):
        res = git_manager.get_status()
        assert res["status"] == "success"

    async def test_github_manager(self):
        res = await github_manager.create_repository(repo_name="kira-test-repo")
        assert res["status"] == "success"
        assert "repository" in res

    def test_docker_manager(self):
        res = docker_manager.generate_dockerfile(project_type="python")
        assert res["status"] == "success"
        assert "Dockerfile" in res["dockerfile_path"]

    def test_vscode_manager(self):
        res = vscode_manager.generate_launch_and_tasks()
        assert res["status"] == "success"

    def test_security_scanner(self):
        res = security_scanner.scan_security()
        assert res["status"] == "success"
        assert "security_score" in res

    # Test Required FastAPI Endpoints
    def test_api_code_analyze(self):
        response = client.post("/code/analyze", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_api_code_generate(self):
        response = client.post("/code/generate", json={"prompt": "Write a Python FastAPI router", "language": "Python"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_api_code_debug(self):
        response = client.post("/code/debug", json={"command": "pytest"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("success", "error_analyzed")

    def test_api_code_test(self):
        response = client.post("/code/test", json={"test_type": "unit"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_api_git_commit(self):
        response = client.post("/git/commit", json={"message": "test: verification commit"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_api_github_repository(self):
        response = client.post("/github/repository", json={"repo_name": "kira-test-api-repo"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_api_docker_build(self):
        response = client.post("/docker/build", json={"tag": "kira-test:latest"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_api_project_create(self):
        response = client.post("/project/create", json={"project_name": "Kira App Test"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_api_security_scan(self):
        response = client.get("/security/scan")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

if __name__ == "__main__":
    unittest.main()
