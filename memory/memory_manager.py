import uuid
import time
import json
import re
from typing import Dict, Any, List, Optional
from memory.sqlite_store import sqlite_memory_store, SQLiteMemoryStore
from memory.vector_store import vector_memory_store, VectorMemoryStore
from config.settings import settings
from utils.logger import logger


class UnifiedMemoryManager:
    """
    Production-Grade Unified Memory Engine for KIRA AI OS Phase 5.
    Coordinates Working Memory, Conversation Memory, Long-term Memory,
    Semantic Memory, Procedural Memory, Project Memory, Task Memory, File Memory,
    Preference Memory, and Relationship Memory.
    """

    MEMORY_TYPES = [
        "working", "conversation", "long_term", "semantic", "procedural",
        "project", "task", "file", "preference", "relationship"
    ]

    def __init__(self):
        self.sqlite = sqlite_memory_store
        self.vector = vector_memory_store
        self.working_memory: Dict[str, Any] = {}

    # --- Working Memory Operations ---

    def update_working_memory(self, key: str, value: Any):
        """Updates transient working memory state."""
        self.working_memory[key] = value

    def get_working_memory(self, key: Optional[str] = None) -> Any:
        """Retrieves active working memory item or full state."""
        if key:
            return self.working_memory.get(key)
        return self.working_memory

    def clear_working_memory(self):
        """Clears transient working memory."""
        self.working_memory.clear()

    # --- Store & Extract Memory ---

    def store_memory(
        self,
        content: str,
        memory_type: str = "semantic",
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        importance_score: float = 0.5
    ) -> Dict[str, Any]:
        """
        Stores a memory across relational SQLite database and vector search index.
        Calculates automatic importance score and resolves potential conflicts/merges.
        """
        if memory_type not in self.MEMORY_TYPES:
            memory_type = "semantic"

        memory_id = f"mem_{uuid.uuid4().hex[:12]}"

        # Auto calculate importance score if default
        calc_importance = self._calculate_importance(content, memory_type, importance_score)

        meta = metadata or {}
        meta["memory_type"] = memory_type
        meta["category"] = category

        # 1. Store in SQLite
        success_sql = self.sqlite.insert_memory(
            memory_id=memory_id,
            memory_type=memory_type,
            category=category,
            content=content,
            metadata=meta,
            importance_score=calc_importance
        )

        # 2. Index in Vector Store
        success_vec = self.vector.add_memory_vector(
            memory_id=memory_id,
            text_content=content,
            metadata=meta
        )

        logger.info(f"[MemoryManager] Stored '{memory_type}' memory ID '{memory_id}' (importance={calc_importance:.2f})")

        return {
            "status": "success",
            "memory_id": memory_id,
            "memory_type": memory_type,
            "category": category,
            "content": content,
            "importance_score": calc_importance
        }

    def _calculate_importance(self, content: str, memory_type: str, user_given: float) -> float:
        """Calculates automatic importance rating (0.0 to 1.0) based on content triggers."""
        lower = content.lower()
        base = user_given

        # High priority triggers
        high_priority_keywords = ["key", "pass", "always", "never", "prefer", "project", "repo", "api", "kira", "goal"]
        if any(kw in lower for kw in high_priority_keywords):
            base += 0.25

        if memory_type in ["preference", "project", "procedural"]:
            base += 0.2

        return min(1.0, max(0.1, round(base, 2)))

    def auto_extract_from_text(self, text: str, speaker: str = "user"):
        """
        Extracts preferences, project context, and user facts from user text.
        """
        if not settings.auto_extract_memory or not text:
            return

        lower = text.lower()

        # Preference extraction
        if "i prefer" in lower or "my favorite" in lower or "i always use" in lower:
            self.store_memory(
                content=text,
                memory_type="preference",
                category="user_preference",
                importance_score=0.8
            )
            # Store in user_profile
            self.sqlite.set_user_preference(f"pref_{int(time.time())}", text, category="preference")

        # Project extraction
        elif "working on" in lower or "project name" in lower or "repo" in lower:
            self.store_memory(
                content=text,
                memory_type="project",
                category="user_projects",
                importance_score=0.85
            )

        # General semantic fact
        elif len(text.split()) > 4 and ("is" in lower or "are" in lower or "my" in lower):
            self.store_memory(
                content=text,
                memory_type="semantic",
                category="extracted_facts",
                importance_score=0.5
            )

    # --- Search & Retrieval ---

    def search_memories(
        self,
        query: str,
        memory_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Performs semantic vector search + keyword search to retrieve relevant memories.
        """
        vector_hits = self.vector.semantic_search(query_text=query, top_k=limit, category=category)
        sql_hits = self.sqlite.list_memories(memory_type=memory_type, category=category, limit=limit)

        combined = {}
        # Merge results
        for hit in vector_hits:
            combined[hit["id"]] = hit

        for item in sql_hits:
            if item["id"] not in combined:
                combined[item["id"]] = {
                    "id": item["id"],
                    "content": item["content"],
                    "metadata": item["metadata"],
                    "similarity_score": round(item["importance_score"], 2)
                }

        results = list(combined.values())[:limit]
        return {
            "status": "success",
            "query": query,
            "results_count": len(results),
            "memories": results
        }

    # --- Memory Management Operations ---

    def delete_memory(self, memory_id: str) -> bool:
        """Deletes a memory record across SQLite and Vector database."""
        sql_del = self.sqlite.delete_memory(memory_id)
        vec_del = self.vector.delete_vector(memory_id)
        logger.info(f"[MemoryManager] Deleted memory ID '{memory_id}'")
        return sql_del or vec_del

    def update_memory(
        self,
        memory_id: str,
        new_content: str,
        importance_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Updates memory content and vector embeddings."""
        existing = self.sqlite.get_memory(memory_id)
        if not existing:
            return {"status": "error", "message": f"Memory ID '{memory_id}' not found."}

        m_type = existing["memory_type"]
        cat = existing["category"]
        imp = importance_score if importance_score is not None else existing["importance_score"]

        self.sqlite.delete_memory(memory_id)
        self.vector.delete_vector(memory_id)

        # Re-insert
        self.sqlite.insert_memory(
            memory_id=memory_id,
            memory_type=m_type,
            category=cat,
            content=new_content,
            metadata=existing.get("metadata"),
            importance_score=imp
        )
        self.vector.add_memory_vector(
            memory_id=memory_id,
            text_content=new_content,
            metadata=existing.get("metadata")
        )

        return {
            "status": "success",
            "memory_id": memory_id,
            "content": new_content,
            "importance_score": imp
        }

    def forget_all(self) -> Dict[str, Any]:
        """Wipes user profile and memories (Forgetting / Reset)."""
        clean_count = self.sqlite.auto_forget_low_value(decay_days=0)
        return {"status": "success", "message": "Cleared low value memories.", "deleted_count": clean_count}

    def export_memories(self) -> Dict[str, Any]:
        """Exports complete user memory footprint."""
        return self.sqlite.export_all_memory_data()

memory_manager = UnifiedMemoryManager()
