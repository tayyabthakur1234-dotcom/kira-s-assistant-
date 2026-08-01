from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from api.models import (
    APIResponse,
    PlannerCreateRequest,
    PlannerRunRequest,
    PlannerStatusRequest,
    TaskActionRequest
)
from planner.graph_planner import graph_planner
from planner.task_manager import task_manager
from planner.agent_executor import agent_executor
from utils.logger import logger

router = APIRouter(prefix="", tags=["Autonomous Planner & Tasks Engine"])


@router.post("/planner/create", response_model=APIResponse)
async def create_plan(req: PlannerCreateRequest):
    """Decomposes a complex high-level goal into an actionable DAG plan with sub-tasks."""
    try:
        decomp = await graph_planner.decompose_goal(req.goal)
        plan_id = decomp["plan_id"]
        tasks = decomp["tasks"]

        # Register in TaskManager
        registered_plan = task_manager.register_plan(plan_id, req.goal, tasks)

        return APIResponse(
            status="success",
            message=f"Plan '{plan_id}' created with {len(tasks)} tasks.",
            data={
                "plan_id": plan_id,
                "goal": req.goal,
                "tasks": tasks,
                "graph_metadata": decomp.get("graph_metadata")
            }
        )
    except Exception as ex:
        logger.error(f"[PlannerRouter] Error in /planner/create: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/planner/run", response_model=APIResponse)
async def run_plan(req: PlannerRunRequest):
    """Executes all DAG tasks in a plan autonomously using Phase 1, 2, 3, 4 engines."""
    try:
        res = await agent_executor.execute_plan(req.plan_id)
        if res.get("status") == "error":
            raise HTTPException(status_code=404, detail=res["message"])

        return APIResponse(
            status="success",
            message=f"Plan '{req.plan_id}' execution completed.",
            data=res
        )
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"[PlannerRouter] Error in /planner/run: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/planner/status", response_model=APIResponse)
async def get_plan_status(req: PlannerStatusRequest):
    """Retrieves real-time progress, completion status, and task list for a plan."""
    try:
        status_info = task_manager.get_plan_status(req.plan_id)
        if not status_info:
            raise HTTPException(status_code=404, detail=f"Plan ID '{req.plan_id}' not found.")

        return APIResponse(
            status="success",
            message=f"Plan '{req.plan_id}' status retrieved.",
            data=status_info
        )
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"[PlannerRouter] Error in /planner/status: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/tasks/list", response_model=APIResponse)
async def list_tasks():
    """Lists all active sub-tasks across registered plans."""
    try:
        tasks = task_manager.list_all_tasks()
        return APIResponse(
            status="success",
            message=f"Retrieved {len(tasks)} tasks.",
            data={"tasks": tasks}
        )
    except Exception as ex:
        logger.error(f"[PlannerRouter] Error in /tasks/list: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/tasks/action", response_model=APIResponse)
async def perform_task_action(req: TaskActionRequest):
    """Performs task or plan management actions ('pause', 'resume', 'cancel')."""
    try:
        res = task_manager.perform_action(req.target_id, req.action)
        if res.get("status") == "error":
            raise HTTPException(status_code=404, detail=res["message"])

        return APIResponse(
            status="success",
            message=f"Action '{req.action}' performed on target '{req.target_id}'.",
            data=res
        )
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"[PlannerRouter] Error in /tasks/action: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
