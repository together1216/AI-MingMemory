"""
记忆管理Agent
"""

import re
import json
from typing import Dict, Any, List
from ..llm.client import LLMClient
from .storage import MemoryStorage


class MemoryAgent:
    """记忆管理Agent"""

    def __init__(self, storage: MemoryStorage, llm_client: LLMClient):
        self.storage = storage
        self.llm_client = llm_client

    def search(self, query: str, limit: int = 5) -> str:
        """搜索相关记忆"""
        results = self.storage.search(query, limit=limit)

        if not results:
            return "无相关记忆"

        formatted = []
        for i, item in enumerate(results, 1):
            content = item.get("content", item.get("summary", ""))[:200]
            formatted.append(f"{i}. {content}...")

        return "\n".join(formatted)

    def save(self, user_input: str, ai_response: str):
        """保存对话到记忆"""
        # 提取关键信息
        extracted = self._extract_key_info(user_input, ai_response)

        # 评分
        importance = self._score_importance(extracted)

        # 存储
        self.storage.add(
            content=f"用户: {user_input}\nAI: {ai_response}",
            summary=extracted.get("summary", user_input[:50]),
            importance=importance,
            tags=extracted.get("tags", []),
            memory_type="episodic",
        )

    def _extract_key_info(self, user_input: str, ai_response: str) -> Dict[str, Any]:
        """提取关键信息"""
        prompt = f"""从以下对话中提取关键信息（JSON格式）：
对话:
用户: {user_input}
AI: {ai_response}

输出格式:
{{
    "summary": "一句话总结",
    "tags": ["标签1", "标签2"],
    "key_facts": ["关键事实1", "关键事实2"],
    "preferences": ["偏好1", "偏好2"]
}}
"""

        try:
            result = self.llm_client.chat([{"role": "user", "content": prompt}])

            # 解析JSON
            json_match = re.search(r"\{.*\}", result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"提取关键信息失败: {e}")

        return {
            "summary": user_input[:50],
            "tags": [],
            "key_facts": [],
            "preferences": [],
        }

    def _score_importance(self, extracted: Dict[str, Any]) -> int:
        """重要性评分"""
        base = 50

        # 根据内容类型调整
        if extracted.get("key_facts"):
            base += 10
        if extracted.get("preferences"):
            base += 20

        return min(base, 100)

    def analyze_periodically(self):
        """定期分析"""
        # 获取近期记忆
        recent = self.storage.get_recent(limit=100)

        if not recent:
            return

        # 生成洞察
        prompt = f"""分析以下记忆，生成洞察：
{[item["content"] for item in recent]}

输出:
1. 行为模式
2. 兴趣趋势
3. 建议关注事项
"""

        try:
            insight = self.llm_client.chat([{"role": "user", "content": prompt}])

            # 保存洞察
            self.storage.add(
                content=insight,
                summary="定期洞察",
                importance=80,
                tags=["insight", "analysis"],
                memory_type="semantic",
            )
        except Exception as e:
            print(f"定期分析失败: {e}")
