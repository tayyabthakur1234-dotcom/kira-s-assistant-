"""
Pair Programming Module - KIRA AI Operating System (Phase 10)
Serves as an expert AI Pair Programmer: explains code logic, recommends refactorings,
generates software design patterns, teaches concepts, and answers complex technical questions.
"""

from typing import Dict, Any, Optional
from utils.logger import logger
from router.model_router import model_router


class PairProgrammingAssistant:
    async def explain_code(self, code_snippet: str, language: str = "TypeScript") -> Dict[str, Any]:
        """Explains code structure, algorithms, and logic in plain language."""
        prompt = f"Explain the following {language} code snippet line-by-line and summarize its main function:\n\n```{language}\n{code_snippet}\n```"
        res = await model_router.execute_with_failover(
            prompt=prompt,
            category="reasoning",
            system_instruction="You are a friendly, expert Senior Software Engineer teaching a colleague."
        )
        return {
            "status": "success",
            "language": language,
            "explanation": res.get("response"),
            "model_used": res.get("model_used")
        }

    async def suggest_refactoring(self, code_snippet: str, goal: str = "Improve readability and performance") -> Dict[str, Any]:
        """Suggests clean architecture refactoring and performance improvements."""
        prompt = f"Goal: {goal}\nRefactor this code using best practices:\n\n```\n{code_snippet}\n```\nProvide refactored code and summary of changes."
        res = await model_router.execute_with_failover(
            prompt=prompt,
            category="coding",
            system_instruction="You are an expert in clean code and software design patterns."
        )
        return {
            "status": "success",
            "goal": goal,
            "refactoring_suggestion": res.get("response")
        }

    async def generate_design_pattern(self, pattern_name: str, language: str = "TypeScript") -> Dict[str, Any]:
        """Generates clean implementation of GoF / Architectural design patterns (e.g. Singleton, Factory, Strategy, Observer)."""
        prompt = f"Generate a complete, practical implementation of the {pattern_name} design pattern in {language}, including usage example."
        res = await model_router.execute_with_failover(
            prompt=prompt,
            category="coding"
        )
        return {
            "status": "success",
            "pattern": pattern_name,
            "language": language,
            "implementation": res.get("response")
        }


pair_programmer = PairProgrammingAssistant()
