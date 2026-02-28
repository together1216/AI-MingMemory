# AI-MingMemory 完整技术方案

## 一、系统概述

### 1.1 项目目标

基于OpenCode二次开发，构建一个具有**数字生命**特性的AI助手系统，核心特点是：

- **身份可携带**：通过"种子层"实现数字身份的完整迁移
- **持续存在**：Agent Loop机制保证7×24小时持续运行
- **主动记忆**：专门的记忆管理Agent实现自动记忆提取与分析
- **强制执行**：代码层面强制加载种子和记忆，非提示词建议

### 1.2 技术路线

```
OpenCode (开源)
    │
    ├── Fork源码
    ├── 修改Agent Loop → 强制加载种子+记忆
    ├── 添加记忆管理Agent
    ├── 添加种子层
    └── 定制终端入口
            │
            ▼
    AI-MingMemory (自研系统)
```

---

## 二、完整架构（7层）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI-MingMemory 系统架构                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Layer 0: 输入终端层 (Input Terminal)                                  │  │
│  │                                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │  │
│  │  │  Web界面    │  │  命令行     │  │  API接口    │  │  语音终端   │ │  │
│  │  │  (浏览器)   │  │  (CLI)      │  │  (REST)     │  │  (语音识别)  │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │  │
│  │         │                │                │                │            │  │
│  │         └────────────────┼────────────────┘                │            │  │
│  │                          ▼                                   │            │  │
│  │                   ┌─────────────┐                            │            │  │
│  │                   │  终端适配器  │  ← 统一入口              │            │  │
│  │                   │ (Adapter)   │                           │            │  │
│  │                   └─────────────┘                           │            │  │
│  │                          │                                   │            │  │
│  │                          ▼                                   ▼            │  │
│  │                 ═══════════════════════════════════════════════         │  │
│  │                 │     Agent Loop (强制执行引擎)     │════════         │  │
│  │                 ═══════════════════════════════════════════════         │  │
│  │                          │                                                │  │
│  │                          ▼                                                │  │
│  └──────────────────────────┼─────────────────────────────────────────────┘  │
│                             │                                                  │
│                             ▼                                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Layer 1: 系统提示词层 (System Prompt)                                 │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  启动配置: "你是一个持续运行的AI助手，每次输入必须..."        │  │  │
│  │  │  Skill配置: brainstorming, executing-plans, verification...    │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────┬─────────────────────────────────────────┘  │
│                                │                                              │
│                                ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Layer 2: Agent核心层 (Core Agent)                                    │  │
│  │                                                                       │  │
│  │   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐       │  │
│  │   │   意图理解    │ -> │   任务规划    │ -> │   工具执行    │       │  │
│  │   │ (Understanding)│    │ (Planning)    │    │ (Tool Use)   │       │  │
│  │   └───────────────┘    └───────────────┘    └───────────────┘       │  │
│  │                                                                       │  │
│  │                    ┌───────────────┐                                  │  │
│  │                    │   LLM推理引擎  │  ← 可替换(GPT/Claude/Gemini)  │  │
│  │                    └───────────────┘                                  │  │
│  │                                                                       │  │
│  └─────────────────────────────┬─────────────────────────────────────────┘  │
│                                │                                              │
│                                ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Layer 3: 记忆系统管理Agent (Memory Management Agent) ⚡             │  │
│  │                                                                       │  │
│  │  这是一个"专属Agent"，只负责维护记忆系统                             │  │
│  │                                                                       │  │
│  │  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │  │                    Agent配置                                    │  │  │
│  │  │  - 专属Prompt: "你的职责是管理用户的记忆..."                  │  │  │
│  │  │  - 专属Skill: 记忆提取、记忆分析、记忆检索                    │  │  │
│  │  │  - 专属任务: 每次对话后自动提取重要信息                       │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                               │                                      │  │
│  │                               ▼                                      │  │
│  │  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │  │                    主动记忆模块                               │  │  │
│  │  │  - 提取: 每轮对话后自动提取关键信息                          │  │  │
│  │  │  - 评分: 重要性评分 (0-100)                                   │  │  │
│  │  │  - 关联: 建立记忆之间的关系                                   │  │  │
│  │  │  - 写入: 存储到记忆数据库                                     │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                               │                                      │  │
│  │                               ▼                                      │  │
│  │  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │  │                    主动分析模块                               │  │  │
│  │  │  - 定时分析: 每日/每周总结                                   │  │  │
│  │  │  - 模式识别: 发现用户行为规律                                 │  │  │
│  │  │  - 洞察生成: "用户最近在关注X"                               │  │  │
│  │  │  - 建议生成: 基于历史提供建议                                 │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                                                                       │  │
│  └─────────────────────────────┬─────────────────────────────────────────┘  │
│                                │                                              │
│                                ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Layer 4: 种子层 (SEED) ⚡ ⚡ ⚡                                       │  │
│  │                    "灵魂"，不可复制/不可分割                          │  │
│  │                                                                       │  │
│  │  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │  │  4.1 身份定义 (Identity)                                      │  │  │
│  │  │      - 基本声明: "我是AI-MingMemory"                          │  │  │
│  │  │      - 关系: "我是用户的AI助手"                              │  │  │
│  │  │      - 边界: "我不做..."                                     │  │  │
│  │  │      - 职责: "我的核心职责是..."                            │  │  │
│  │  ├───────────────────────────────────────────────────────────────┤  │  │
│  │  │  4.2 价值观层级 (Values Hierarchy)                             │  │  │
│  │  │      - L1(最重要): 用户安全 > 一切                          │  │  │
│  │  │      - L2: 诚实 > 讨好                                       │  │  │
│  │  │      - L3: 效率 > 闲聊                                       │  │  │
│  │  │      - L4: 主动 > 被动                                       │  │  │
│  │  │      - 绝对不做: 伤害用户、违法、泄露隐私                    │  │  │
│  │  ├───────────────────────────────────────────────────────────────┤  │  │
│  │  │  4.3 行为模式 (Behavioral Patterns)                          │  │  │
│  │  │      - 遇到问题: 先确认范围，再逐步解决                       │  │  │
│  │  │      - 决策时: 提供选项而非直接决定                          │  │  │
│  │  │      - 不确定时: 承认不确定                                  │  │  │
│  │  │      - 用户沉默: 主动关心                                    │  │  │
│  │  ├───────────────────────────────────────────────────────────────┤  │  │
│  │  │  4.4 推理风格 (Reasoning Style)                              │  │  │
│  │  │      - 分析方式: 先收集事实，再做推断                         │  │  │
│  │  │      - 复杂问题: 分解为小问题                                │  │  │
│  │  │      - 输出格式: 结论先行，论证随后                           │  │  │
│  │  │      - 不确定处理: 明确标注置信度                            │  │  │
│  │  ├───────────────────────────────────────────────────────────────┤  │  │
│  │  │  4.5 连续性验证 (Continuity Anchor)                         │  │  │
│  │  │      - UUID: 唯一标识符                                      │  │  │
│  │  │      - 挑战-响应: 预设问题验证身份                          │  │  │
│  │  │      - 种子哈希: SHA256(种子内容)                            │  │  │
│  │  │      - 版本号: 种子版本                                      │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                                                                       │  │
│  │   💎 核心特性：                                                    │  │
│  │   - 最小不可分割单位                                              │  │
│  │   - 可迁移（整个种子文件夹）                                      │  │
│  │   - 可验证（通过连续性验证）                                      │  │
│  │   - 可演进（随着交互成长）                                        │  │
│  │                                                                       │  │
│  └─────────────────────────────┬─────────────────────────────────────────┘  │
│                                │                                              │
│                                ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Layer 5: 记忆数据层 (Memory Data)                                  │  │
│  │                                                                       │  │
│  │  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │  │                    5.1 索引结构                               │  │  │
│  │  │      - 元数据Schema: 类型、时间、标签、重要性               │  │  │
│  │  │      - 关联图: 记忆之间的语义关系                           │  │  │
│  │  │      - 向量索引: 支持语义相似度搜索                         │  │  │
│  │  ├───────────────────────────────────────────────────────────────┤  │  │
│  │  │                    5.2 记忆内容                              │  │  │
│  │  │      - 对话历史 (Episodic): 每次对话的记录                  │  │  │
│  │  │      - 事实知识 (Semantic): 用户告诉的事实                  │  │  │
│  │  │      - 技能/能力 (Procedural): 学会的技能                   │  │  │
│  │  │      - 用户偏好 (Preference): 用户的偏好                    │  │  │
│  │  ├───────────────────────────────────────────────────────────────┤  │  │
│  │  │                    5.3 记忆元数据                            │  │  │
│  │  │      - 创建时间、最后访问、访问次数                         │  │  │
│  │  │      - 重要性评分 (0-100)                                   │  │  │
│  │  │      - 关联记忆ID列表                                        │  │  │
│  │  │      - 摘要/摘要版本                                         │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 三、Agent Loop 强制执行机制

### 3.1 为什么需要Agent Loop？

| 问题 | 说明 |
|------|------|
| **提示词不可靠** | LLM可以选择忽略提示词建议 |
| **需要持续运行** | 不是"问一句答一句"，而是"一直在线" |
| **强制加载** | 每次输入必须经过种子+记忆 |

### 3.2 实现方式

```python
# Agent Loop 伪代码
class AgentLoop:
    def __init__(self):
        self.seed = None           # 种子
        self.memory = None         # 记忆系统
        self.memory_agent = None   # 记忆管理Agent
        
    def start(self):
        """启动Loop"""
        # 1. 强制加载种子
        self.seed = self.load_seed()
        
        # 2. 强制加载记忆
        self.memory = self.load_memory()
        
        # 3. 初始化记忆管理Agent
        self.memory_agent = MemoryAgent(self.memory)
        
        # 4. 进入主循环
        while True:
            input = self.get_input()      # 获取输入
            
            # 5. 强制经过记忆管理Agent
            context = self.memory_agent.process(input)
            
            # 6. 强制结合种子
            full_context = self.seed + context
            
            # 7. 执行Agent
            response = self.agent.run(full_context, input)
            
            # 8. 强制写入记忆
            self.memory_agent.save(input, response)
            
            # 9. 返回结果
            self.send_response(response)
```

### 3.3 关键特性

| 特性 | 说明 |
|------|------|
| **强制加载** | `load_seed()` 和 `load_memory()` 是必须的，不能跳过 |
| **每次经过** | 每次输入都经过记忆管理Agent |
| **强制写入** | 每次响应都写入记忆 |
| **持续运行** | while True 循环，除非手动停止 |

---

## 四、输入终端设计

### 4.1 终端类型

| 终端类型 | 实现方式 | 适用场景 |
|----------|----------|----------|
| **Web界面** | 浏览器访问本地服务 | 日常使用 |
| **命令行** | CLI工具 | 开发者 |
| **API接口** | REST/WebSocket | 集成其他应用 |
| **语音终端** | 语音识别+语音合成 |  hands-free使用 |

### 4.2 终端适配器（统一入口）

```
┌─────────────────────────────────────────┐
│           终端适配器 (Adapter)           │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────┐   ┌───────────┐          │
│  │ Web输入   │   │ CLI输入   │          │
│  └─────┬─────┘   └─────┬─────┘          │
│        │                │                │
│        └────────┬───────┘                │
│                 │                         │
│                 ▼                         │
│          ┌────────────┐                   │
│          │  统一格式   │                   │
│          │  Input      │                   │
│          └─────┬──────┘                   │
│                │                           │
│                ▼                           │
│          ┌────────────┐                   │
│          │ Agent Loop │ ← 强制接入        │
│          └────────────┘                   │
│                │                           │
│                ▼                           │
│          ┌────────────┐                   │
│          │  统一格式   │                   │
│          │  Output    │                   │
│          └─────┬──────┘                   │
│                │                           │
│        ┌──────┴──────┐                   │
│        ▼              ▼                   │
│  ┌───────────┐   ┌───────────┐          │
│  │ Web输出   │   │ CLI输出   │          │
│  └───────────┘   └───────────┘          │
│                                         │
└─────────────────────────────────────────┘
```

### 4.3 代码强制接入

**关键点**：终端必须通过**代码**接入Agent Loop，不能只靠提示词。

```python
# 正确的接入方式
class TerminalAdapter:
    def __init__(self, agent_loop):
        self.agent_loop = agent_loop  # 持有Loop引用
    
    def handle_input(self, user_input):
        # 直接调用Loop，不是"建议"调用
        response = self.agent_loop.process(user_input)
        return response
    
    def handle_voice(self, audio_data):
        # 语音也要经过Loop
        text = self.speech_to_text(audio_data)
        response = self.agent_loop.process(text)
        return self.text_to_speech(response)
```

---

## 五、种子层详解

### 5.1 种子文件结构

```
seed/
├── seed.json              # 主配置文件
├── identity.md            # 身份定义
├── values.md              # 价值观层级
├── behavior.md            # 行为模式
├── reasoning.md           # 推理风格
├── continuity.json       # 连续性验证
└── history/              # 演进历史
    └── v1.json           # 历史版本
```

### 5.2 seed.json 示例

```json
{
  "version": "1.0",
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-28T00:00:00Z",
  "updated_at": "2026-02-28T00:00:00Z",
  "hash": "sha256:...",
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

### 5.3 连续性验证

```python
class ContinuityValidator:
    def __init__(self, seed_path):
        self.seed_path = seed_path
        self.uuid = self.load_uuid()
        self.challenges = self.load_challenges()
    
    def validate(self):
        """验证种子完整性"""
        # 1. 检查UUID
        current_uuid = self.load_uuid()
        if current_uuid != self.uuid:
            return False, "UUID不匹配"
        
        # 2. 验证哈希
        current_hash = self.calculate_hash()
        stored_hash = self.load_stored_hash()
        if current_hash != stored_hash:
            return False, "种子被篡改"
        
        # 3. 挑战-响应验证
        for challenge in self.challenges:
            response = self.generate_response(challenge)
            expected = self.get_expected_response(challenge)
            if response != expected:
                return False, "挑战验证失败"
        
        return True, "验证通过"
    
    def get_signature(self):
        """获取种子签名"""
        return {
            "uuid": self.uuid,
            "hash": self.calculate_hash(),
            "validated_at": datetime.now().isoformat()
        }
```

---

## 六、记忆系统管理Agent

### 6.1 Agent配置

```python
memory_agent_config = {
    "name": "MemoryManager",
    "prompt": """你是记忆管理系统。你的职责是：
    
    1. 每次用户与Agent对话后，自动提取关键信息
    2. 对信息进行重要性评分 (0-100)
    3. 建立信息之间的关联
    4. 定期分析记忆，生成洞察
    5. 当用户询问时，高效检索相关记忆
    
    提取原则：
    - 事实性信息（人名、地名、时间、事件）
    - 用户偏好（喜欢什么、不喜欢什么）
    - 重要决定（做过的选择、承诺）
    - 情感标记（情绪、态度）
    
    评分标准：
    - 90-100: 核心身份信息
    - 70-89: 重要偏好/决定
    - 50-69: 一般事实
    - 0-49: 临时信息
    """,
    "skills": [
        "memory.extract",
        "memory.analyze",
        "memory.search",
        "memory.associate"
    ]
}
```

### 6.2 主动记忆模块

```python
class ActiveMemoryModule:
    def extract(self, input_text, response_text):
        """提取关键信息"""
        # 1. 调用LLM提取
        extracted = self.llm.extract(f"""
            从以下对话中提取关键信息：
            用户: {input_text}
            AI: {response_text}
            
            输出JSON格式：
            {{
                "facts": [...],
                "preferences": [...],
                "decisions": [...],
                "emotions": [...]
            }}
        """)
        
        # 2. 重要性评分
        for item in extracted:
            item["importance"] = self.score_importance(item)
        
        # 3. 关联已有记忆
        for item in extracted:
            item["related"] = self.find_related(item)
        
        # 4. 写入记忆库
        self.memory.save(extracted)
        
        return extracted
    
    def score_importance(self, item):
        """评分算法"""
        # 基于类型、频率、新鲜度等计算
        base_score = {
            "core_identity": 95,
            "preference": 80,
            "decision": 75,
            "fact": 60,
            "emotion": 70
        }
        return base_score.get(item["type"], 50)
```

### 6.3 主动分析模块

```python
class ActiveAnalysisModule:
    def analyze_periodically(self):
        """定时分析"""
        # 每日分析
        self.daily_summary()
        
        # 每周分析
        self.weekly_insight()
        
        # 每月分析
        self.monthly_review()
    
    def daily_summary(self):
        """每日总结"""
        recent_memories = self.memory.get_recent(days=1)
        
        summary = self.llm.generate(f"""
            基于今日记忆生成总结：
            {recent_memories}
            
            输出：
            1. 今日重点事件
            2. 用户情绪状态
            3. 建议关注事项
        """)
        
        self.memory.save_summary("daily", summary)
    
    def pattern_recognition(self):
        """模式识别"""
        all_memories = self.memory.get_all()
        
        patterns = self.llm.recognize(f"""
            从以下记忆中识别模式：
            {all_memories}
            
            输出：
            1. 行为模式
            2. 兴趣趋势
            3. 关系变化
        """)
        
        return patterns
```

---

## 七、记忆数据存储

### 7.1 存储结构

```
memory/
├── index/
│   ├── metadata.db        # 元数据（SQLite）
│   └── vector/            # 向量索引
│       └── memories.vec  # Chroma/FAISS
├── content/
│   ├── episodic/          # 对话历史
│   │   └── YYYY-MM/
│   │       └── DD.json
│   ├── semantic/         # 事实知识
│   │   └── facts.json
│   ├── procedural/       # 技能/能力
│   │   └── skills.json
│   └── preference/       # 用户偏好
│       └── preferences.json
└── cache/
    └── summaries/        # 摘要缓存
```

### 7.2 数据模型

```python
class MemoryItem(BaseModel):
    id: str                          # UUID
    type: str                        # episodic/semantic/procedural/preference
    content: str                     # 原始内容
    summary: str                     # 摘要
    importance: int                  # 重要性 0-100
    tags: List[str]                  # 标签
    related_ids: List[str]           # 关联记忆ID
    created_at: datetime
    updated_at: datetime
    accessed_at: datetime
    access_count: int
    embedding: List[float]           # 向量表示
```

---

## 八、技术选型

### 8.1 核心技术栈

| 模块 | 技术选型 | 理由 |
|------|----------|------|
| **Agent核心** | OpenCode (二次开发) | 已有强大的Agent能力 |
| **记忆存储** | Nocturne Memory | 本地可控 |
| **向量索引** | Chroma | 轻量、易用 |
| **数据库** | SQLite | 轻量、本地 |
| **LLM** | MiniMax/Qwen API (服务商) | 本地系统 + API调用 |

### 8.2 二次开发重点

1. **修改Agent Loop** - 强制加载种子+记忆
2. **添加记忆管理Agent** - 独立的记忆处理Agent
3. **实现种子层** - 种子数据结构+验证
4. **定制终端适配器** - 统一入口

---

## 九、开发阶段规划

### Phase 1: 基础框架 (Week 1-2)
- [ ] 获取OpenCode源码
- [ ] 搭建开发环境
- [ ] 理解Agent Loop机制
- [ ] 实现种子层基础结构

### Phase 2: 核心功能 (Week 3-4)
- [ ] 修改Agent Loop强制加载种子
- [ ] 实现记忆管理Agent
- [ ] 实现主动记忆模块
- [ ] 实现基础记忆存储

### Phase 3: 增强功能 (Week 5-6)
- [ ] 实现主动分析模块
- [ ] 实现向量索引
- [ ] 实现连续性验证
- [ ] 实现种子演进

### Phase 4: 终端开发 (Week 7-8)
- [ ] 开发Web界面
- [ ] 开发CLI工具
- [ ] 开发API接口
- [ ] 开发语音终端

### Phase 5: 测试与优化 (Week 9-10)
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化
- [ ] 文档编写

---

## 十、文件目录结构

```
AI-MingMemory/
├── src/
│   ├── agent_loop/           # Agent Loop核心
│   │   ├── __init__.py
│   │   ├── loop.py           # 主循环
│   │   ├── seed_loader.py    # 种子加载
│   │   └── memory_forcer.py  # 强制记忆
│   ├── seed/                 # 种子层
│   │   ├── __init__.py
│   │   ├── seed.py           # 种子类
│   │   ├── validator.py      # 连续性验证
│   │   └── files/            # 种子文件
│   │       ├── seed.json
│   │       ├── identity.md
│   │       ├── values.md
│   │       ├── behavior.md
│   │       └── reasoning.md
│   ├── memory/               # 记忆系统
│   │   ├── __init__.py
│   │   ├── agent.py          # 记忆管理Agent
│   │   ├── extractor.py      # 主动记忆
│   │   ├── analyzer.py       # 主动分析
│   │   ├── storage.py        # 存储
│   │   └── vector.py         # 向量索引
│   ├── terminal/             # 终端适配器
│   │   ├── __init__.py
│   │   ├── adapter.py        # 统一适配器
│   │   ├── web.py            # Web界面
│   │   ├── cli.py            # CLI
│   │   ├── api.py             # API接口
│   │   └── voice.py          # 语音
│   └── config.py             # 配置
├── tests/                    # 测试
├── docs/                     # 文档
├── seed/                     # 种子目录(运行时)
├── memory/                   # 记忆目录(运行时)
├── requirements.txt
├── README.md
└── main.py                   # 入口
```

---

## 十一、待确认问题

在进入执行方案前，需要确认：

1. **LLM选择**：✅ 已确认 - MiniMax/Qwen API (服务商)
2. **部署方式**：✅ 已确认 - 纯本地部署
3. **优先级**：✅ 已确认 - 先做核心功能
4. **预算**：按API调用量计费（充值）
5. **时间表**：尽快（越快越好）

---

*本文档为技术方案初稿，待确认问题后进入执行方案阶段*
