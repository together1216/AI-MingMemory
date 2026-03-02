# AI-MingMemory 执行方案

## 执行概览

| 阶段 | 内容 | 预计时间 |
|------|------|----------|
| **Phase 1** | 准备与环境搭建 | Day 1 |
| **Phase 2** | 种子层实现 | Day 2-3 |
| **Phase 3** | Agent Loop 强制执行 | Day 4-5 |
| **Phase 4** | 记忆管理Agent | Day 6-7 |
| **Phase 5** | 基础记忆存储 | Day 8-9 |
| **Phase 6** | 主动记忆模块 | Day 10 |

---

## Phase 1: 准备与环境搭建

### Day 1 任务清单

#### 1.1 获取OpenCode源码

```bash
# 克隆OpenCode源码到本地
git clone https://github.com/your-repo/opencode.git AI-MingMemory-core

# 或者Fork后再克隆
git clone https://github.com/YOUR_USERNAME/opencode.git AI-MingMemory-core
```

#### 1.2 创建项目结构

```
AI-MingMemory/
├── src/
│   ├── agent_loop/           # Agent Loop核心
│   │   ├── __init__.py
│   │   ├── loop.py
│   │   ├── seed_loader.py
│   │   └── memory_forcer.py
│   ├── seed/                 # 种子层
│   │   ├── __init__.py
│   │   ├── seed.py
│   │   ├── validator.py
│   │   └── files/
│   │       └── seed.json
│   ├── memory/               # 记忆系统
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── extractor.py
│   │   ├── storage.py
│   │   └── vector.py
│   ├── terminal/             # 终端适配器
│   │   ├── __init__.py
│   │   └── adapter.py
│   └── config.py
├── seed/                     # 运行时种子目录
├── memory/                   # 运行时记忆目录
├── config.yaml               # 配置文件
├── requirements.txt
└── main.py                   # 入口
```

#### 1.3 安装依赖

```bash
# requirements.txt
opencode>=1.0.0
pyyaml>=6.0
sqlalchemy>=2.0
chromadb>=0.4.0
requests>=2.31.0
pydantic>=2.0
python-dotenv>=1.0
```

```bash
pip install -r requirements.txt
```

#### 1.4 配置文件

```yaml
# config.yaml
llm:
  provider: "minimax"  # 或 qwen
  api_key: "${MINIMAX_API_KEY}"  # 环境变量
  base_url: "https://api.minimax.chat/v1"
  model: "abab6.5s-chat"

system:
  seed_path: "./seed"
  memory_path: "./memory"
  auto_backup: true
  backup_interval: 3600  # 秒

agent_loop:
 强制记忆: true
 强制种子: true
 log_level: "INFO"
```

---

## Phase 2: 种子层实现

### Day 2-3 任务清单

#### 2.1 创建种子文件

```json
// seed/seed.json
{
  "version": "1.0",
  "uuid": "generate-uuid-v4",
  "created_at": "2026-02-28T00:00:00Z",
  "updated_at": "2026-02-28T00:00:00Z",
  "hash": "",
  "identity": {
    "name": "AI-MingMemory",
    "role": "用户的AI助手",
    "boundaries": [
      "不提供非法建议",
      "不伤害用户",
      "不泄露隐私"
    ]
  },
  "values": {
    "level_1": "用户安全 > 一切",
    "level_2": "诚实 > 讨好",
    "level_3": "效率 > 闲聊",
    "never_do": [
      "伤害用户",
      "违法",
      "泄露隐私"
    ]
  },
  "behavior_patterns": [
    {
      "condition": "遇到问题",
      "response": "先确认范围，再逐步解决"
    },
    {
      "condition": "决策时",
      "response": "提供选项而非直接决定"
    },
    {
      "condition": "不确定时",
      "response": "承认不确定"
    }
  ],
  "reasoning_style": {
    "analysis": "先收集事实，再做推断",
    "complex": "分解为小问题",
    "output": "结论先行，论证随后",
    "uncertainty": "明确标注置信度"
  }
}
```

#### 2.2 种子类实现

```python
# src/seed/seed.py
import json
import hashlib
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel


class Identity(BaseModel):
    name: str
    role: str
    boundaries: list[str]


class Values(BaseModel):
    level_1: str
    level_2: str
    level_3: str
    never_do: list[str]


class BehaviorPattern(BaseModel):
    condition: str
    response: str


class ReasoningStyle(BaseModel):
    analysis: str
    complex: str
    output: str
    uncertainty: str


class Seed(BaseModel):
    version: str
    uuid: str
    created_at: str
    updated_at: str
    hash: str = ""
    identity: Identity
    values: Values
    behavior_patterns: list[BehaviorPattern]
    reasoning_style: ReasoningStyle

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
        self.hash = self.calculate_hash()
        
        path = Path(seed_path) / "seed.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, ensure_ascii=False, indent=2)

    def calculate_hash(self) -> str:
        """计算种子哈希"""
        content = self.model_dump_json()
        return hashlib.sha256(content.encode()).hexdigest()

    def to_prompt(self) -> str:
        """转换为系统提示词"""
        prompt = f"""你是 {self.identity.name}，{self.identity.role}。

核心价值观：
- {self.values.level_1}
- {self.values.level_2}
- {self.values.level_3}

绝对不做：
{chr(10).join(f"- {item}" for item in self.values.never_do)}

行为模式：
{chr(10).join(f"- 遇到{pattern.condition}时: {pattern.response}" for pattern in self.behavior_patterns)}

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
            identity=Identity(
                name=name,
                role="用户的AI助手",
                boundaries=["不提供非法建议", "不伤害用户", "不泄露隐私"]
            ),
            values=Values(
                level_1="用户安全 > 一切",
                level_2="诚实 > 讨好",
                level_3="效率 > 闲聊",
                never_do=["伤害用户", "违法", "泄露隐私"]
            ),
            behavior_patterns=[
                BehaviorPattern(condition="问题", response="先确认范围，再逐步解决"),
                BehaviorPattern(condition="决策", response="提供选项而非直接决定"),
                BehaviorPattern(condition="不确定", response="承认不确定")
            ],
            reasoning_style=ReasoningStyle(
                analysis="先收集事实，再做推断",
                complex="分解为小问题",
                output="结论先行，论证随后",
                uncertainty="明确标注置信度"
            )
        )
        seed.save(seed_path)
        return seed
```

#### 2.3 连续性验证

```python
# src/seed/validator.py
import hashlib
from typing import Tuple
from .seed import Seed


class ContinuityValidator:
    """连续性验证器"""
    
    def __init__(self, seed: Seed):
        self.seed = seed
        self.original_hash = seed.hash
        self.original_uuid = seed.uuid
    
    def validate(self) -> Tuple[bool, str]:
        """验证种子完整性"""
        # 1. 验证UUID
        if self.seed.uuid != self.original_uuid:
            return False, "UUID不匹配: 种子身份失效"
        
        # 2. 验证哈希
        current_hash = self.seed.calculate_hash()
        if current_hash != self.original_hash:
            return False, "哈希不匹配: 种子被篡改"
        
        # 3. 验证必要字段
        if not self.seed.identity.name:
            return False, "身份名称缺失"
        
        return True, "验证通过"
    
    def get_signature(self) -> dict:
        """获取种子签名"""
        return {
            "uuid": self.seed.uuid,
            "hash": self.seed.hash,
            "name": self.seed.identity.name,
            "validated_at": self.seed.updated_at
        }
```

---

## Phase 3: Agent Loop 强制执行

### Day 4-5 任务清单

#### 3.1 LLM客户端

```python
# src/llm/client.py
import os
import requests
from typing import Optional, Dict, Any


class LLMClient:
    def __init__(self, config: Dict[str, Any]):
        self.provider = config.get("provider", "minimax")
        self.api_key = os.getenv(config.get("api_key", "MINIMAX_API_KEY"))
        self.base_url = config.get("base_url", "https://api.minimax.chat/v1")
        self.model = config.get("model", "abab6.5s-chat")
    
    def chat(self, messages: list, **kwargs) -> str:
        """发送聊天请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM调用失败: {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    @classmethod
    def from_config(cls, config_path: str = "config.yaml") -> "LLMClient":
        """从配置文件创建"""
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return cls(config["llm"])
```

#### 3.2 Agent Loop核心

```python
# src/agent_loop/loop.py
from typing import Optional, Dict, Any
from ..seed.seed import Seed
from ..seed.validator import ContinuityValidator
from ..memory.agent import MemoryAgent
from ..llm.client import LLMClient


class AgentLoop:
    """Agent Loop - 强制执行引擎"""
    
    def __init__(
        self,
        seed: Seed,
        memory_agent: MemoryAgent,
        llm_client: LLMClient,
        config: Dict[str, Any]
    ):
        self.seed = seed
        self.memory_agent = memory_agent
        self.llm_client = llm_client
        self.config = config
        self.validator = ContinuityValidator(seed)
        
        # 验证种子
        valid, msg = self.validator.validate()
        if not valid:
            raise ValueError(f"种子验证失败: {msg}")
    
    def process(self, user_input: str) -> str:
        """处理用户输入 - 强制经过所有环节"""
        
        # Step 1: 强制加载种子
        seed_prompt = self.seed.to_prompt()
        
        # Step 2: 强制查询记忆
        memory_context = self.memory_agent.search(user_input)
        
        # Step 3: 构建完整上下文
        system_prompt = f"{seed_prompt}\n\n相关记忆:\n{memory_context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # Step 4: 调用LLM
        response = self.llm_client.chat(messages)
        
        # Step 5: 强制写入记忆
        self.memory_agent.save(user_input, response)
        
        return response
    
    def run_interactive(self):
        """交互式运行"""
        print(f"🤖 {self.seed.identity.name} 已启动 (输入 'quit' 退出)")
        print(f"📋 种子: {self.seed.uuid}")
        print("-" * 50)
        
        while True:
            user_input = input("\n👤 你: ").strip()
            
            if user_input.lower() in ["quit", "exit", "退出"]:
                print("👋 再见!")
                break
            
            if not user_input:
                continue
            
            try:
                response = self.process(user_input)
                print(f"\n🤖 AI: {response}")
            except Exception as e:
                print(f"\n❌ 错误: {e}")
```

---

## Phase 4: 记忆管理Agent

### Day 6-7 任务清单

#### 4.1 记忆管理Agent

```python
# src/memory/agent.py
from typing import List, Dict, Any
from ..llm.client import LLMClient


class MemoryAgent:
    """记忆管理Agent"""
    
    def __init__(self, storage: "MemoryStorage", llm_client: LLMClient):
        self.storage = storage
        self.llm_client = llm_client
    
    def search(self, query: str, limit: int = 5) -> str:
        """搜索相关记忆"""
        results = self.storage.search(query, limit=limit)
        
        if not results:
            return "无相关记忆"
        
        formatted = []
        for i, item in enumerate(results, 1):
            formatted.append(f"{i}. {item['content'][:200]}...")
        
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
            summary=extracted.get("summary", ""),
            importance=importance,
            tags=extracted.get("tags", []),
            memory_type="episodic"
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
            result = self.llm_client.chat([
                {"role": "user", "content": prompt}
            ])
            
            # 解析JSON（简化版）
            import json
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"summary": user_input[:50], "tags": [], "key_facts": [], "preferences": []}
    
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
{[item['content'] for item in recent]}

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
                memory_type="semantic"
            )
        except:
            pass
```

---

## Phase 5: 基础记忆存储

### Day 8-9 任务清单

#### 5.1 记忆存储

```python
# src/memory/storage.py
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
        memory_type: str = "episodic"
    ) -> str:
        """添加记忆"""
        memory_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memories 
            (id, content, summary, importance, tags, memory_type, created_at, accessed_at, access_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (memory_id, content, summary, importance, json.dumps(tags or []), memory_type, now, now))
        
        conn.commit()
        conn.close()
        
        return memory_id
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索记忆（简化版：按重要性+时间）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM memories
            ORDER BY importance DESC, access_count DESC, created_at DESC
            LIMIT ?
        """, (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        
        # 更新访问次数
        for item in results:
            cursor.execute("""
                UPDATE memories 
                SET access_count = access_count + 1, accessed_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), item["id"]))
        
        conn.commit()
        conn.close()
        
        return results
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取近期记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM memories
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
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
```

---

## Phase 6: 主动记忆模块

### Day 10 任务清单

#### 6.1 主动记忆模块

```python
# src/memory/extractor.py
from typing import List, Dict, Any
from .storage import MemoryStorage


class ActiveMemoryExtractor:
    """主动记忆提取器"""
    
    def __init__(self, storage: MemoryStorage):
        self.storage = storage
    
    def process_conversation(self, user_input: str, ai_response: str):
        """处理对话后自动提取"""
        # 这个功能已经整合到 MemoryAgent 中
        # 这里是备用逻辑
        pass
    
    def cleanup_low_importance(self, threshold: int = 10):
        """清理低重要性记忆"""
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM memories 
            WHERE importance < ? AND access_count < 3
        """, (threshold,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def compress_old_memories(self, days: int = 30):
        """压缩旧记忆"""
        # 简化实现：可以定期生成摘要
        pass
```

---

## 主入口

```python
# main.py
import argparse
import yaml
from pathlib import Path

from src.seed.seed import Seed
from src.seed.validator import ContinuityValidator
from src.memory.storage import MemoryStorage
from src.memory.agent import MemoryAgent
from src.llm.client import LLMClient
from src.agent_loop.loop import AgentLoop


def main():
    parser = argparse.ArgumentParser(description="AI-MingMemory")
    parser.add_argument("--config", default="config.yaml", help="配置文件")
    parser.add_argument("--init-seed", action="store_true", help="初始化种子")
    args = parser.parse_args()
    
    # 加载配置
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    seed_path = config["system"]["seed_path"]
    memory_path = config["system"]["memory_path"]
    
    # 初始化或加载种子
    if args.init_seed or not Path(seed_path).exists():
        print("📦 创建新种子...")
        seed = Seed.create_new(seed_path)
        print(f"✅ 种子已创建: {seed.uuid}")
    else:
        print("📂 加载种子...")
        seed = Seed.load(seed_path)
        print(f"✅ 种子已加载: {seed.uuid}")
    
    # 初始化记忆存储
    memory_storage = MemoryStorage(memory_path)
    
    # 初始化LLM客户端
    llm_client = LLMClient.from_config(args.config)
    
    # 初始化记忆管理Agent
    memory_agent = MemoryAgent(memory_storage, llm_client)
    
    # 初始化Agent Loop
    agent_loop = AgentLoop(seed, memory_agent, llm_client, config)
    
    # 启动
    print(f"\n🚀 {seed.identity.name} 启动完成!\n")
    agent_loop.run_interactive()


if __name__ == "__main__":
    main()
```

---

## 快速开始

```bash
# 1. 克隆/下载OpenCode源码

# 2. 安装依赖
pip install -r requirements.txt

# 3. 复制配置
cp config.example.yaml config.yaml

# 4. 编辑配置（填入API Key）
# config.yaml 中设置 MINIMAX_API_KEY 环境变量
export MINIMAX_API_KEY="your-api-key"

# 5. 初始化种子
python main.py --init-seed

# 6. 运行
python main.py
```

---

*执行方案完成，等待开始开发*
