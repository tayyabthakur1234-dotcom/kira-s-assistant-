"""
FastAPI Router for Phase 10 - Developer Intelligence Engine
Provides endpoints for Code Analysis, Code Generation, Debugging, Testing,
Git, GitHub, Docker, Project Management, VS Code Workspace, Pair Programming, and Security Audit.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from developer.dev_intelligence import dev_intelligence
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

router = APIRouter(prefix="", tags=["Phase 10 - Developer Intelligence Engine"])


# Request Models
class AnalyzeCodeRequest(BaseModel):
    target_dir: Optional[str] = Field(default=None, description="Optional target directory to analyze")

class GenerateCodeRequest(BaseModel):
    prompt: str = Field(..., description="Prompt describing code to generate")
    language: str = Field(default="TypeScript", description="Language e.g. Python, TypeScript, React, Go, Rust")
    component_type: str = Field(default="file", description="Component type e.g. file, class, function, api, test, doc")
    target_path: Optional[str] = Field(default=None, description="Optional relative output file path")
    context_files: Optional[List[str]] = Field(default=None, description="Optional list of context files")

class DebugCodeRequest(BaseModel):
    command: Optional[str] = Field(default=None, description="Optional command to execute and capture errors e.g. npm run build")
    stack_trace: Optional[str] = Field(default=None, description="Optional raw error stack trace text")
    file_context: Optional[str] = Field(default=None, description="Optional source code context")
    auto_apply_fix: bool = Field(default=False, description="Automatically write suggested fix to disk")

class TestCodeRequest(BaseModel):
    test_type: str = Field(default="unit", description="unit | integration | api | browser | performance | security | all")
    test_path: Optional[str] = Field(default=None, description="Optional target test file or directory")

class GitCommitRequest(BaseModel):
    message: Optional[str] = Field(default=None, description="Commit message. If omitted, AI auto-generates conventional commit")
    files: Optional[List[str]] = Field(default=None, description="List of files to stage, or all if empty")

class GitHubRepoRequest(BaseModel):
    repo_name: str = Field(..., description="Name of repository")
    description: str = Field(default="Created by KIRA Developer Intelligence", description="Repo description")
    private: bool = Field(default=False, description="Whether repository is private")

class DockerBuildRequest(BaseModel):
    tag: str = Field(default="kira-app:latest", description="Image tag")

class CreateProjectRequest(BaseModel):
    project_name: str = Field(..., description="Name of new project")
    tech_stack: str = Field(default="TypeScript / React / Express / Python", description="Tech stack description")
    template: str = Field(default="fullstack", description="Project template")

class PairExplainRequest(BaseModel):
    code_snippet: str = Field(..., description="Source code snippet to explain")
    language: str = Field(default="TypeScript", description="Language of snippet")

class PairRefactorRequest(BaseModel):
    code_snippet: str = Field(..., description="Source code to refactor")
    goal: str = Field(default="Improve readability and performance", description="Refactoring goal")

class VSCodeSymbolRequest(BaseModel):
    query: str = Field(..., description="Symbol or function name to search in workspace")


# Endpoints

@router.post("/code/analyze", summary="Analyze codebase architecture, bugs, code smells, duplicate code, and complexity")
async def analyze_code(req: AnalyzeCodeRequest):
    return code_analyzer.analyze_codebase(req.target_dir)

@router.post("/code/generate", summary="Generate clean production-ready code, classes, functions, or tests in 18 supported languages")
async def generate_code_endpoint(req: GenerateCodeRequest):
    return await code_generator.generate_code(
        prompt=req.prompt,
        language=req.language,
        component_type=req.component_type,
        target_path=req.target_path,
        context_files=req.context_files
    )

@router.post("/code/debug", summary="Run project, capture errors, perform AI root cause analysis, suggest and apply fixes")
async def debug_code_endpoint(req: DebugCodeRequest):
    return await debugger.debug_project(
        command=req.command,
        stack_trace=req.stack_trace,
        file_context=req.file_context,
        auto_apply_fix=req.auto_apply_fix
    )

@router.post("/code/test", summary="Execute and generate unit, integration, API, and Playwright browser tests")
async def test_code_endpoint(req: TestCodeRequest):
    return await testing_engine.run_tests(
        test_type=req.test_type,
        test_path=req.test_path
    )

@router.post("/git/commit", summary="Stage files and create Git commit with AI-generated conventional commit message")
async def git_commit_endpoint(req: GitCommitRequest):
    return await git_manager.commit_changes(
        message=req.message,
        files=req.files
    )

@router.post("/github/repository", summary="Create or manage GitHub repositories, issues, and pull requests")
async def github_repository_endpoint(req: GitHubRepoRequest):
    return await github_manager.create_repository(
        repo_name=req.repo_name,
        description=req.description,
        private=req.private
    )

@router.post("/docker/build", summary="Generate Dockerfiles and docker-compose files and build container images")
async def docker_build_endpoint(req: DockerBuildRequest):
    return docker_manager.build_image(tag=req.tag)

@router.post("/project/create", summary="Scaffold complete multi-language project structure, requirements, README, and manifests")
async def create_project_endpoint(req: CreateProjectRequest):
    return await project_manager.create_project(
        project_name=req.project_name,
        tech_stack=req.tech_stack,
        template=req.template
    )

@router.get("/security/scan", summary="Scan workspace for leaked secrets, API keys, and dependency security risks")
async def security_scan_endpoint():
    return security_scanner.scan_security()

@router.post("/pair/explain", summary="AI Pair Programming code explanation and logic walk-through")
async def pair_explain_endpoint(req: PairExplainRequest):
    return await pair_programmer.explain_code(
        code_snippet=req.code_snippet,
        language=req.language
    )

@router.post("/pair/refactor", summary="AI Pair Programming clean architecture code refactoring")
async def pair_refactor_endpoint(req: PairRefactorRequest):
    return await pair_programmer.suggest_refactoring(
        code_snippet=req.code_snippet,
        goal=req.goal
    )

@router.post("/vscode/symbols", summary="Navigate symbols and definitions across the VS Code workspace")
async def vscode_symbols_endpoint(req: VSCodeSymbolRequest):
    return vscode_manager.navigate_symbols(query=req.query)

@router.post("/vscode/configs", summary="Generate VS Code launch.json and tasks.json configs")
async def vscode_configs_endpoint():
    return vscode_manager.generate_launch_and_tasks()
