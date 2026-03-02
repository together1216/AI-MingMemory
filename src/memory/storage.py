"""
记忆存储 - SQLite实现
"""

import json
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class MemoryStorage:
    """记忆存储"""

    def __init__(self, memory_path: str):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)

        self.db_path = self.memory_path / "memories.db"
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                summary TEXT,
                importance INTEGER DEFAULT 50,
                tags TEXT,
                memory_type TEXT DEFAULT 'episodic',
                created_at TEXT,
                accessed_at TEXT,
                access_count INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_importance 
            ON memories(importance DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created 
            ON memories(created_at DESC)
        """)

        conn.commit()
        conn.close()

    def add(
        self,
        content: str,
        summary: str = "",
        importance: int = 50,
        tags: List[str] = None,
        memory_type: str = "episodic",
    ) -> str:
        """添加记忆"""
        memory_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO memories 
            (id, content, summary, importance, tags, memory_type, created_at, accessed_at, access_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
            (
                memory_id,
                content,
                summary,
                importance,
                json.dumps(tags or []),
                memory_type,
                now,
                now,
            ),
        )

        conn.commit()
        conn.close()

        return memory_id

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索记忆（简化版：按重要性+时间）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM memories
            ORDER BY importance DESC, access_count DESC, created_at DESC
            LIMIT ?
        """,
            (limit,),
        )

        results = [dict(row) for row in cursor.fetchall()]

        # 更新访问次数
        for item in results:
            cursor.execute(
                """
                UPDATE memories 
                SET access_count = access_count + 1, accessed_at = ?
                WHERE id = ?
            """,
                (datetime.now().isoformat(), item["id"]),
            )

        conn.commit()
        conn.close()

        return results

    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取近期记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM memories
            ORDER BY created_at DESC
            LIMIT ?
        """,
            (limit,),
        )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM memories
            ORDER BY importance DESC, created_at DESC
        """)

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def count(self) -> int:
        """获取记忆总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        conn.close()
        return count
