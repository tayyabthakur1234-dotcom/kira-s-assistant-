from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from api.models import (
    APIResponse,
    MemoryStoreRequest,
    MemorySearchRequest,
    MemoryDeleteRequest,
    MemoryUpdateRequest
)
from memory.memory_manager import memory_manager
from utils.logger import logger

router = APIRouter(prefix="/memory", tags=["Memory & Intelligence Engine"])


@router.post("/store", response_model=APIResponse)
async def store_memory(req: MemoryStoreRequest):
    """Stores a memory entry in relational SQLite and vector search index."""
    try:
        res = memory_manager.store_memory(
            content=req.content,
            memory_type=req.memory_type,
            category=req.category,
            metadata=req.metadata,
            importance_score=req.importance_score
        )
        return APIResponse(
            status="success",
            message="Memory successfully stored and indexed.",
            data=res
        )
    except Exception as ex:
        logger.error(f"[MemoryRouter] Error in /memory/store: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/search", response_model=APIResponse)
async def search_memories(req: MemorySearchRequest):
    """Executes semantic vector search + keyword search to retrieve relevant memories."""
    try:
        res = memory_manager.search_memories(
            query=req.query,
            memory_type=req.memory_type,
            category=req.category,
            limit=req.limit
        )
        return APIResponse(
            status="success",
            message=f"Found {res['results_count']} relevant memories.",
            data=res
        )
    except Exception as ex:
        logger.error(f"[MemoryRouter] Error in /memory/search: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/delete", response_model=APIResponse)
async def delete_memory(req: MemoryDeleteRequest):
    """Deletes a memory record across SQLite database and vector search index."""
    try:
        success = memory_manager.delete_memory(req.memory_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Memory ID '{req.memory_id}' not found.")
        return APIResponse(
            status="success",
            message=f"Memory ID '{req.memory_id}' deleted successfully.",
            data={"memory_id": req.memory_id}
        )
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"[MemoryRouter] Error in /memory/delete: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/update", response_model=APIResponse)
async def update_memory(req: MemoryUpdateRequest):
    """Updates memory content and re-indexes vector embeddings."""
    try:
        res = memory_manager.update_memory(
            memory_id=req.memory_id,
            new_content=req.new_content,
            importance_score=req.importance_score
        )
        if res.get("status") == "error":
            raise HTTPException(status_code=404, detail=res["message"])
        return APIResponse(
            status="success",
            message="Memory updated and re-indexed.",
            data=res
        )
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"[MemoryRouter] Error in /memory/update: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/export", response_model=APIResponse)
async def export_memories():
    """Exports complete memory footprint including user profile and semantic records."""
    try:
        export_data = memory_manager.export_memories()
        return APIResponse(
            status="success",
            message="Memory footprint exported successfully.",
            data=export_data
        )
    except Exception as ex:
        logger.error(f"[MemoryRouter] Error in /memory/export: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/forget", response_model=APIResponse)
async def forget_low_value_memories():
    """Triggers automatic memory decay / cleanup of stale, low-value memories."""
    try:
        res = memory_manager.forget_all()
        return APIResponse(
            status="success",
            message="Low value stale memories cleaned up.",
            data=res
        )
    except Exception as ex:
        logger.error(f"[MemoryRouter] Error in /memory/forget: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
