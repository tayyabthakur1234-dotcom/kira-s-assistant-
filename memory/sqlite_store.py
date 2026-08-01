import sqlite3
import json
import time
import os
from typing import Dict, Any, List, Optional
from config.settings import settings
from utils.logger import logger


class SQLiteMemoryStore:
    """
    Relational SQLite Persistent Storage for KIRA AI OS Phase 5 Memory Engine.
    Stores User Profile, Preferences, Projects, Goals, Skills, Installed Software,
    Apps, GitHub Repos, Files, Custom Commands, and Conversation History.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes database tables if they do not exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 1. User Profile & Preferences
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_profile (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        category TEXT DEFAULT 'general',
                        updated_at REAL NOT NULL
                    )
                """)

                # 2. Memories Store (Semantic, Procedural, Preference, Relationship, Project, Task, File)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        memory_type TEXT NOT NULL,
                        category TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata TEXT,
                        importance_score REAL DEFAULT 0.5,
                        access_count INTEGER DEFAULT 1,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    )
                """)

                # 3. Conversation Logs
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        speaker TEXT NOT NULL,
                        message TEXT NOT NULL,
                        intent TEXT,
                        timestamp REAL NOT NULL
                    )
                """)

                # 4. Custom Commands & System Shortcuts
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custom_commands (
                        trigger TEXT PRIMARY KEY,
                        action_type TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        description TEXT
                    )
                """)

                # 5. Lessons Learned / Procedural Reflections
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS lessons_learned (
                        id TEXT PRIMARY KEY,
                        task_goal TEXT NOT NULL,
                        error_encountered TEXT,
                        resolution_strategy TEXT NOT NULL,
                        success_rate REAL DEFAULT 1.0,
                        created_at REAL NOT NULL
                    )
                """)

                conn.commit()
                logger.info(f"[SQLiteMemory] Initialized database schema at '{self.db_path}'")
        except Exception as e:
            logger.error(f"[SQLiteMemory] Schema initialization error: {e}")

    # --- User Profile & Preferences Operations ---

    def set_user_preference(self, key: str, value: Any, category: str = "general") -> bool:
        """Stores or updates a user profile preference attribute."""
        try:
            val_str = json.dumps(value) if not isinstance(value, str) else value
            now = time.time()
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO user_profile (key, value, category, updated_at) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value, category=excluded.category, updated_at=excluded.updated_at",
                    (key, val_str, category, now)
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"[SQLiteMemory] Error setting preference '{key}': {e}")
            return False

    def get_user_preference(self, key: str) -> Optional[Any]:
        """Retrieves user preference value by key."""
        try:
            with self._get_connection() as conn:
                row = conn.execute("SELECT value FROM user_profile WHERE key = ?", (key,)).fetchone()
                if row:
                    val = row["value"]
                    try:
                        return json.loads(val)
                    except Exception:
                        return val
        except Exception as e:
            logger.error(f"[SQLiteMemory] Error getting preference '{key}': {e}")
        return None

    def get_all_user_profile(self) -> Dict[str, Any]:
        """Returns all stored user profile attributes."""
        profile = {}
        try:
            with self._get_connection() as conn:
                rows = conn.execute("SELECT key, value, category FROM user_profile").fetchall()
                for row in rows:
                    val = row["value"]
                    try:
                        val = json.loads(val)
                    except Exception:
                        pass
                    profile[row["key"]] = val
        except Exception as e:
            logger.error(f"[SQLiteMemory] Error reading user profile: {e}")
        return profile

    # --- Generic Memory CRUD ---

    def insert_memory(
        self,
        memory_id: str,
        memory_type: str,
        category: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        importance_score: float = 0.5
    ) -> bool:
        """Inserts a structured memory record into SQLite."""
        try:
            now = time.time()
            meta_str = json.dumps(metadata or {})
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO memories (id, memory_type, category, content, metadata, importance_score, access_count, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)",
                    (memory_id, memory_type, category, content, meta_str, importance_score, now, now)
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"[SQLiteMemory] Error inserting memory '{memory_id}': {e}")
            return False

    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single memory record by ID and increments access count."""
        try:
            with self._get_connection() as conn:
                row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
                if row:
                    conn.execute(
                        "UPDATE memories SET access_count = access_count + 1, updated_at = ? WHERE id = ?",
                        (time.time(), memory_id)
                    )
                    conn.commit()
                    return {
                        "id": row["id"],
                        "memory_type": row["memory_type"],
                        "category": row["category"],
                        "content": row["content"],
                        "metadata": json.loads(row["metadata"] or "{}"),
                        "importance_score": row["importance_score"],
                        "access_count": row["access_count"] + 1,
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    }
        except Exception as e:
            logger.error(f"[SQLiteMemory] Error getting memory '{memory_id}': {e}")
        return None

    def list_memories(
        self,
        memory_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists memories filtered by memory_type or category."""
        results = []
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM memories WHERE 1=1"
                params = []
                if memory_type:
                    query += " AND memory_type = ?"
                    params.append(memory_type)
                if category:
                    query += " AND category = ?"
                    params.append(category)
                query += " ORDER BY importance_score DESC, updated_at DESC LIMIT ?"
                params.append(limit)

                rows = conn.execute(query, params).fetchall()
                for row in rows:
                    results.append({
                        "id": row["id"],
                        "memory_type": row["memory_type"],
                        "category": row["category"],
                        "content": row["content"],
                        "metadata": json.loads(row["metadata"] or "{}"),
                        "importance_score": row["importance_score"],
                        "access_count": row["access_count"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    })
        except Exception as e:
            logger.error(f"[SQLiteMemory] Error listing memories: {e}")
        return results

    def delete_memory(self, memory_id: str) -> bool:
        """Deletes a memory record by ID."""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"[SQLiteMemory] Error deleting memory '{memory_id}': {e}")
            return False

    def auto_forget_low_value(self, decay_days: int = 30) -> int:
        """
        Deletes low-value, unaccessed old memories (importance < 0.3 and inactive > decay_days).
        """
        threshold_time = time.time() - (decay_days * 86400)
        deleted_count = 0
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM memories WHERE importance_score < 0.3 AND updated_at < ? AND access_count <= 2",
                    (threshold_time,)
                )
                deleted_count = cursor.rowcount
                conn.commit()
            logger.info(f"[SQLiteMemory] Auto-forget cleaned up {deleted_count} stale memories.")
        except Exception as e:
            logger.error(f"[SQLiteMemory] Auto-forget error: {e}")
        return deleted_count

    # --- Conversation History ---

    def log_conversation(self, session_id: str, speaker: str, message: str, intent: Optional[str] = None):
        """Logs a conversation message line."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO conversation_history (session_id, speaker, message, intent, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (session_id, speaker, message, intent, time.time())
                )
                conn.commit()
        except Exception as e:
            logger.error(f"[SQLiteMemory] Error logging conversation: {e}")

    def get_recent_conversations(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves recent conversation history for a given session."""
        results = []
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    "SELECT speaker, message, intent, timestamp FROM conversation_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                    (session_id, limit)
                ).fetchall()
                for row in reversed(rows):
                    results.append({
                        "speaker": row["speaker"],
                        "message": row["message"],
                        "intent": row["intent"],
                        "timestamp": row["timestamp"]
                    })
        except Exception as e:
            logger.error(f"[SQLiteMemory] Error fetching recent conversations: {e}")
        return results

    # --- Lessons Learned / Reflections ---

    def store_lesson(self, lesson_id: str, goal: str, strategy: str, error: Optional[str] = None):
        """Stores a reflection lesson learned from task execution."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO lessons_learned (id, task_goal, error_encountered, resolution_strategy, success_rate, created_at) "
                    "VALUES (?, ?, ?, ?, 1.0, ?)",
                    (lesson_id, goal, error, strategy, time.time())
                )
                conn.commit()
        except Exception as e:
            logger.error(f"[SQLiteMemory] Error storing lesson: {e}")

    def export_all_memory_data(self) -> Dict[str, Any]:
        """Exports full database contents to JSON export dict."""
        return {
            "user_profile": self.get_all_user_profile(),
            "memories": self.list_memories(limit=1000),
            "export_timestamp": time.time()
        }

sqlite_memory_store = SQLiteMemoryStore()
