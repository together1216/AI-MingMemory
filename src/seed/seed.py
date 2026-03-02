"""
种子类 - 数字生命的核心身份
"""

import json
import hashlib
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class Identity(BaseModel):
    """身份定义"""

    name: str = Field(default="AI-MingMemory", description="AI名称")
    role: str = Field(default="用户的AI助手", description="角色")
    boundaries: List[str] = Field(
        default_factory=lambda: ["不提供非法建议", "不伤害用户", "不泄露隐私"],
        description="边界",
    )


class Values(BaseModel):
    """价值观层级"""

    level_1: str = Field(default="用户安全 > 一切", description="第一优先级")
    level_2: str = Field(default="诚实 > 讨好", description="第二优先级")
    level_3: str = Field(default="效率 > 闲聊", description="第三优先级")
    never_do: List[str] = Field(
        default_factory=lambda: ["伤害用户", "违法", "泄露隐私"],
        description="绝对不做的事",
    )


class BehaviorPattern(BaseModel):
    """行为模式"""

    condition: str = Field(description="条件")
    response: str = Field(description="反应")


class ReasoningStyle(BaseModel):
    """推理风格"""

    analysis: str = Field(default="先收集事实，再做推断", description="分析方式")
    complex: str = Field(default="分解为小问题", description="复杂问题处理")
    output: str = Field(default="结论先行，论证随后", description="输出格式")
    uncertainty: str = Field(default="明确标注置信度", description="不确定性处理")


class Seed(BaseModel):
    """种子 - 数字生命的核心身份"""

    version: str = Field(default="1.0", description="版本")
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), description="唯一标识")
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat() + "Z", description="创建时间"
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat() + "Z", description="更新时间"
    )
    hash: str = Field(default="", description="种子哈希")

    identity: Identity = Field(default_factory=Identity)
    values: Values = Field(default_factory=Values)
    behavior_patterns: List[BehaviorPattern] = Field(default_factory=list)
    reasoning_style: ReasoningStyle = Field(default_factory=ReasoningStyle)

    @classmethod
    def load(cls, seed_path: str) -> "Seed":
        """从文件加载种子"""
        path = Path(seed_path) / "seed.json"
        if not path.exists():
            raise FileNotFoundError(f"种子文件不存在: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(**data)

    def save(self, seed_path: str):
        """保存种子到文件"""
        self.updated_at = datetime.now().isoformat() + "Z"
        # 计算哈希时不包含hash字段本身
        self.hash = self.calculate_hash(include_hash=False)

        path = Path(seed_path) / "seed.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, ensure_ascii=False, indent=2)

    def calculate_hash(self, include_hash: bool = False) -> str:
        """计算种子哈希"""
        data = self.model_dump()
        if not include_hash:
            data.pop('hash', None)
        content = json.dumps(data, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def to_prompt(self) -> str:
        """转换为系统提示词"""
        behavior_text = "\n".join(
            [
                f"- 遇到{pattern.condition}时: {pattern.response}"
                for pattern in self.behavior_patterns
            ]
        )

        prompt = f"""你是 {self.identity.name}，{self.identity.role}。

核心价值观：
- {self.values.level_1}
- {self.values.level_2}
- {self.values.level_3}

绝对不做：
{chr(10).join(f"- {item}" for item in self.values.never_do)}

行为模式：
{behavior_text}

推理风格：
- 分析方式: {self.reasoning_style.analysis}
- 复杂问题: {self.reasoning_style.complex}
- 输出格式: {self.reasoning_style.output}
- 不确定处理: {self.reasoning_style.uncertainty}
"""
        return prompt

    @classmethod
    def create_new(cls, seed_path: str, name: str = "AI-MingMemory") -> "Seed":
        """创建新种子"""
        seed = cls(
            version="1.0",
            uuid=str(uuid.uuid4()),
            created_at=datetime.now().isoformat() + "Z",
            updated_at=datetime.now().isoformat() + "Z",
            hash="",
            identity=Identity(name=name, role="用户的AI助手"),
            values=Values(),
            behavior_patterns=[
                BehaviorPattern(condition="问题", response="先确认范围，再逐步解决"),
                BehaviorPattern(condition="决策", response="提供选项而非直接决定"),
                BehaviorPattern(condition="不确定", response="承认不确定"),
                BehaviorPattern(condition="用户沉默", response="主动关心"),
            ],
            reasoning_style=ReasoningStyle(),
        )
        seed.save(seed_path)
        return seed
