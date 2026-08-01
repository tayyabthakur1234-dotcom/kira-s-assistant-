import uuid
import time
from typing import Dict, Any, Optional
from memory.memory_manager import memory_manager
from utils.logger import logger


class SelfReflectionEngine:
    """
    Self Reflection & Continuous Learning Engine for KIRA AI OS Phase 5.
    Evaluates execution outputs, detects errors or unexpected edge cases,
    derives resolution insights, and saves lessons learned into procedural memory.
    """

    def evaluate_task_execution(
        self,
        task_id: str,
        goal: str,
        execution_output: Dict[str, Any],
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates task execution result, calculates success confidence, and logs procedural lesson.
        """
        lesson_id = f"lesson_{uuid.uuid4().hex[:8]}"
        is_success = error is None and execution_output.get("status") in ["success", "completed"]

        if is_success:
            strategy = f"Successfully executed goal using engine '{execution_output.get('engine', 'auto')}'."
            reflection_summary = f"Goal '{goal}' achieved cleanly without errors."
        else:
            strategy = f"Faced issue: {error or 'Unknown error'}. Recommended retry with Vision Engine fallback."
            reflection_summary = f"Execution faced roadblock: {error}. Logged fallback pattern."

        # Store lesson into SQLite and Vector Memory
        memory_manager.sqlite.store_lesson(
            lesson_id=lesson_id,
            goal=goal,
            strategy=strategy,
            error=error
        )

        memory_manager.store_memory(
            content=f"Reflection Lesson ({goal}): {strategy}",
            memory_type="procedural",
            category="lessons_learned",
            importance_score=0.85
        )

        logger.info(f"[SelfReflection] Evaluated task '{task_id}' (success={is_success}). Stored lesson '{lesson_id}'.")

        return {
            "status": "success",
            "lesson_id": lesson_id,
            "is_success": is_success,
            "reflection_summary": reflection_summary,
            "strategy": strategy
        }

reflection_engine = SelfReflectionEngine()
