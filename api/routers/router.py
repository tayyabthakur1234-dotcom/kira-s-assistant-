from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from router.model_router import model_router

router = APIRouter(prefix="", tags=["KIRA AI - Phase 12 (Final Enterprise Release) - AI Model Router"])

class ModelRouteRequest(BaseModel):
    prompt: str = Field(..., description="User prompt or instruction")
    has_image: bool = Field(default=False, description="Whether prompt includes visual screenshot/image input")
    force_local: bool = Field(default=False, description="Force routing to local Ollama model")

class TaskExecutionRequest(BaseModel):
    prompt: str = Field(..., description="Task instruction")
    category_override: Optional[str] = Field(default=None, description="Optional explicit category override")
    system_instruction: Optional[str] = Field(default=None, description="System persona or instruction")

class ModelSelectOverrideRequest(BaseModel):
    category: str = Field(..., description="Request category (e.g. coding, vision, reasoning)")
    preferred_model: str = Field(..., description="Model ID to set as primary (e.g. grok-4, gemini-2.5-pro)")

@router.post("/router/model", summary="Analyze prompt and return optimal AI model routing decision")
async def route_model(req: ModelRouteRequest):
    category = model_router.classify_request(req.prompt, has_image=req.has_image, force_local=req.force_local)
    candidates = model_router.select_model(category)
    return {
        "status": "success",
        "category": category,
        "recommended_primary_model": candidates[0],
        "fallback_chain": candidates[1:],
        "force_local": req.force_local
    }

@router.post("/router/task", summary="Execute task prompt with intelligent model routing and automatic failover")
async def execute_task_with_router(req: TaskExecutionRequest):
    category = req.category_override or model_router.classify_request(req.prompt)
    result = await model_router.execute_with_failover(
        prompt=req.prompt,
        category=category,
        system_instruction=req.system_instruction
    )
    return result

@router.get("/models/status", summary="Get health check, latency, and availability across all supported AI models")
async def get_models_status():
    models = model_router.get_supported_models_status()
    return {
        "status": "success",
        "total_supported_models": len(models),
        "models": models
    }

@router.post("/models/select", summary="Override primary model priority for a specific request category")
async def select_model_override(req: ModelSelectOverrideRequest):
    model_router.user_overrides[req.category] = req.preferred_model
    return {
        "status": "success",
        "category": req.category,
        "primary_override": req.preferred_model,
        "message": f"Successfully set {req.preferred_model} as primary model for {req.category} tasks."
    }
