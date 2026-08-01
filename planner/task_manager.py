import time
import asyncio
from typing import Dict, Any, List, Optional
from utils.logger import logger


class TaskManager:
    """
    Task Lifecycle & State Control Manager for KIRA AI OS Phase 5.
    Tracks task creation, execution statuses (pending, running, paused, completed, failed, cancelled),
    retries, execution logs, and priority ordering.
    """

    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_PAUSED = "paused"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    def __init__(self):
        self.plans: Dict[str, Dict[str, Any]] = {}
        self.active_tasks: Dict[str, Dict[str, Any]] = {}

    def register_plan(self, plan_id: str, goal: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Registers a new plan decomposition and its task DAG nodes."""
        plan_record = {
            "plan_id": plan_id,
            "goal": goal,
            "status": self.STATUS_PENDING,
            "created_at": time.time(),
            "updated_at": time.time(),
            "tasks": {}
        }

        for task in tasks:
            t_id = task["id"]
            t_record = {
                "id": t_id,
                "plan_id": plan_id,
                "title": task.get("title", f"Task {t_id}"),
                "description": task.get("description", ""),
                "engine": task.get("engine", "desktop"),
                "dependencies": task.get("dependencies", []),
                "status": self.STATUS_PENDING,
                "retries": 0,
                "max_retries": 3,
                "result": None,
                "error": None,
                "created_at": time.time(),
                "updated_at": time.time()
            }
            plan_record["tasks"][t_id] = t_record
            self.active_tasks[t_id] = t_record

        self.plans[plan_id] = plan_record
        logger.info(f"[TaskManager] Registered plan '{plan_id}' with {len(tasks)} sub-tasks.")
        return plan_record

    def get_plan_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves overall status and progress of a plan."""
        plan = self.plans.get(plan_id)
        if not plan:
            return None

        tasks_list = list(plan["tasks"].values())
        completed_count = sum(1 for t in tasks_list if t["status"] == self.STATUS_COMPLETED)
        failed_count = sum(1 for t in tasks_list if t["status"] == self.STATUS_FAILED)
        total_count = len(tasks_list)

        progress_pct = round((completed_count / total_count * 100.0), 1) if total_count > 0 else 0.0

        return {
            "plan_id": plan_id,
            "goal": plan["goal"],
            "status": plan["status"],
            "progress_percent": progress_pct,
            "completed_tasks": completed_count,
            "failed_tasks": failed_count,
            "total_tasks": total_count,
            "tasks": tasks_list,
            "created_at": plan["created_at"],
            "updated_at": plan["updated_at"]
        }

    def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """Updates status of an individual task."""
        task = self.active_tasks.get(task_id)
        if not task:
            return False

        task["status"] = status
        task["updated_at"] = time.time()
        if result:
            task["result"] = result
        if error:
            task["error"] = error

        # Update parent plan status
        plan = self.plans.get(task["plan_id"])
        if plan:
            plan["updated_at"] = time.time()
            all_statuses = [t["status"] for t in plan["tasks"].values()]
            if all(s == self.STATUS_COMPLETED for s in all_statuses):
                plan["status"] = self.STATUS_COMPLETED
            elif any(s == self.STATUS_FAILED for s in all_statuses):
                plan["status"] = self.STATUS_FAILED
            elif any(s == self.STATUS_RUNNING for s in all_statuses):
                plan["status"] = self.STATUS_RUNNING

        logger.info(f"[TaskManager] Task '{task_id}' updated to status '{status}'.")
        return True

    def perform_action(self, target_id: str, action: str) -> Dict[str, Any]:
        """
        Performs management control action ('pause', 'resume', 'cancel') on plan or task.
        """
        action = action.lower()

        # Action on Plan
        if target_id in self.plans:
            plan = self.plans[target_id]
            if action == "pause":
                plan["status"] = self.STATUS_PAUSED
            elif action == "resume":
                plan["status"] = self.STATUS_RUNNING
            elif action == "cancel":
                plan["status"] = self.STATUS_CANCELLED
                for t in plan["tasks"].values():
                    t["status"] = self.STATUS_CANCELLED

            return {"status": "success", "target_id": target_id, "action": action, "new_status": plan["status"]}

        # Action on Task
        if target_id in self.active_tasks:
            task = self.active_tasks[target_id]
            if action == "pause":
                task["status"] = self.STATUS_PAUSED
            elif action == "resume":
                task["status"] = self.STATUS_PENDING
            elif action == "cancel":
                task["status"] = self.STATUS_CANCELLED

            return {"status": "success", "target_id": target_id, "action": action, "new_status": task["status"]}

        return {"status": "error", "message": f"Target ID '{target_id}' not found."}

    def list_all_tasks(self) -> List[Dict[str, Any]]:
        """Returns list of all active tasks across plans."""
        return list(self.active_tasks.values())

task_manager = TaskManager()
