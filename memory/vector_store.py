import math
import os
import json
import time
from typing import Dict, Any, List, Optional
from config.settings import settings
from utils.logger import logger

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except ImportError:
    chromadb = None


class VectorMemoryStore:
    """
    ChromaDB & Embedding Vector Storage Engine for KIRA AI OS Phase 5 Memory.
    Provides semantic vector indexing and similarity search across semantic memories,
    procedural knowledge, past goals, preferences, and relationships.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or settings.vector_db_dir
        self.client = None
        self.collection = None
        self._fallback_vectors: List[Dict[str, Any]] = []
        self._init_vector_db()

    def _init_vector_db(self):
        """Initializes ChromaDB persistent client and memory collection."""
        if chromadb:
            try:
                os.makedirs(self.persist_dir, exist_ok=True)
                self.client = chromadb.PersistentClient(path=self.persist_dir)
                self.collection = self.client.get_or_create_collection(
                    name="kira_semantic_memories",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"[VectorMemory] ChromaDB collection initialized at '{self.persist_dir}'")
                return
            except Exception as e:
                logger.warning(f"[VectorMemory] ChromaDB setup warning: {e}. Running in memory fallback vector mode.")

        logger.info("[VectorMemory] Initialized in-memory fallback vector search.")

    def _simple_embedding(self, text: str) -> List[float]:
        """
        Calculates simple character/word ngram normalized frequency vector for fallback embedding.
        """
        words = text.lower().split()
        vector = [0.0] * 32
        for w in words:
            idx = sum(ord(c) for c in w) % 32
            vector[idx] += 1.0

        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def add_memory_vector(
        self,
        memory_id: str,
        text_content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Indexes memory text into vector store with associated metadata."""
        if not text_content:
            return False

        meta = metadata or {}
        meta_clean = {k: str(v) for k, v in meta.items()}

        if self.collection:
            try:
                self.collection.upsert(
                    ids=[memory_id],
                    documents=[text_content],
                    metadatas=[meta_clean]
                )
                return True
            except Exception as e:
                logger.error(f"[VectorMemory] ChromaDB upsert error: {e}")

        # Fallback store
        emb = self._simple_embedding(text_content)
        # Update if exists
        self._fallback_vectors = [v for v in self._fallback_vectors if v["id"] != memory_id]
        self._fallback_vectors.append({
            "id": memory_id,
            "document": text_content,
            "metadata": meta_clean,
            "embedding": emb
        })
        return True

    def semantic_search(
        self,
        query_text: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic vector similarity search against stored memories.
        """
        if not query_text:
            return []

        if self.collection:
            try:
                where_filter = {"category": category} if category else None
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=top_k,
                    where=where_filter
                )

                hits = []
                ids = results.get("ids", [[]])[0]
                docs = results.get("documents", [[]])[0]
                metas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0] if "distances" in results else [0.0] * len(ids)

                for i in range(len(ids)):
                    hits.append({
                        "id": ids[i],
                        "content": docs[i],
                        "metadata": metas[i],
                        "similarity_score": round(1.0 - float(distances[i]), 3) if i < len(distances) else 0.8
                    })
                return hits
            except Exception as e:
                logger.error(f"[VectorMemory] ChromaDB query error: {e}")

        # Fallback cosine search
        q_emb = self._simple_embedding(query_text)
        scored = []
        for item in self._fallback_vectors:
            if category and item["metadata"].get("category") != category:
                continue
            dot = sum(a * b for a, b in zip(q_emb, item["embedding"]))
            scored.append((dot, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, item in scored[:top_k]:
            results.append({
                "id": item["id"],
                "content": item["document"],
                "metadata": item["metadata"],
                "similarity_score": round(score, 3)
            })
        return results

    def delete_vector(self, memory_id: str) -> bool:
        """Deletes vector record from database."""
        if self.collection:
            try:
                self.collection.delete(ids=[memory_id])
            except Exception:
                pass

        self._fallback_vectors = [v for v in self._fallback_vectors if v["id"] != memory_id]
        return True

vector_memory_store = VectorMemoryStore()
