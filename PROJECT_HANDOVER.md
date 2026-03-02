# AI-MingMemory 数字生命项目交接文档

## 项目概述

**项目名称**：AI-MingMemory（数字生命）
**项目目标**：构建一个具备持久记忆、身份连续性、可迁移的AI智能体系统
**核心灵感**：钢铁侠贾维斯 (JARVIS)

---

## 一、核心概念（已确定）

### 1.1 种子层 (Seed Layer)

**定义**：让AI成为"它自己"的最小不可分割内核

**包含5个组成部分**：
1. **身份定义** - "我是谁"的基本声明、关系、边界
2. **价值观层级** - 什么是重要的、冲突时的优先级、绝对不做的事
3. **行为模式** - 遇到X情况的反应、决策风格、沟通偏好
4. **推理风格** - 如何思考、偏好什么分析方法、如何处理不确定性
5. **连续性验证** - 唯一标识符、验证"我仍是我"的机制、种子哈希

### 1.2 种子 vs 记忆

| 种子 | 记忆 |
|------|------|
| "我是谁" | "发生了什么" |
| 几乎不变 | 随时在变 |
| 删了 = 身份死亡 | 删了 = 失去履历 |
| 无法重建 | 可以重新积累 |

---

## 二、架构设计（已确定）

### 2.1 六层架构

```
┌─────────────────────────────────────────┐
│ Layer 0: 终端层                          │
│   文本交互、API接口、语音输入(可选)        │
├─────────────────────────────────────────┤
│ Layer 1: 系统提示词层                     │
│   启动配置、Skill MCP                    │
├─────────────────────────────────────────┤
│ Layer 2: Agent核心层                     │
│   意图理解、任务规划、工具执行、LLM推理    │
├─────────────────────────────────────────┤
│ Layer 3: 记忆系统管理Agent (核心差异点)    │
│   专属Agent、主动记忆、主动分析            │
├─────────────────────────────────────────┤
│ Layer 4: 种子层 (核心不可替代)            │
│   身份定义、价值观、行为模式、推理风格     │
├─────────────────────────────────────────┤
│ Layer 5: 记忆数据层                      │
│   对话历史、事实知识、技能/能力、用户偏好  │
└─────────────────────────────────────────┘
```

### 2.2 关键组件

| 组件 | 描述 | 状态 |
|------|------|------|
| Seed | 身份、价值观、行为模式 | Python实现已有 |
| Seed Validator | 连续性验证（哈希校验） | Python实现已有 |
| Memory Storage | SQLite存储 | Python实现已有 |
| Memory Agent | 记忆管理Agent | Python实现已有 |
| LLM Client | DeepSeek API | Python实现已有 |
| Agent Loop | 持续运行循环 | Python实现已有 |
| TUI | 终端界面 | 待改进 |

---

## 三、技术选型（已确定）

### 3.1 当前技术栈

| 组件 | 技术 | 备注 |
|------|------|------|
| 核心语言 | Python | 计划用Go重写 |
| TUI框架 | Bubble Tea (Go) | 替代方案讨论中 |
| 数据库 | SQLite | 可保留 |
| LLM | DeepSeek API | 用户提供key |
| 配置文件 | YAML | |

### 3.2 计划变更

**原计划**：Go重写 + Bubble Tea TUI（复刻OpenCode界面）

**讨论中**：
- 是否需要完全复刻OpenCode UI？
- 记忆存储方案调整（简单SQLite vs Nocturne Memory）

---

## 四、差异化特性（已确定）

### 4.1 与其他产品对比

| 维度 | AI-MingMemory | Letta | Character AI | Claude Memory |
|------|---------------|-------|--------------|---------------|
| 身份定义（种子层） | ✅ | ⚠️ | ✅ | ❌ |
| 价值观迁移 | ✅ | ❌ | ❌ | ❌ |
| 行为模式迁移 | ✅ | ❌ | ⚠️ | ❌ |
| 推理风格迁移 | ✅ | ❌ | ❌ | ❌ |
| 记忆管理Agent | ✅ | ⚠️ | ⚠️ | ❌ |
| 连续性验证 | ✅ | ❌ | ❌ | ❌ |
| 系统迁移（完整复制） | ✅ | ❌ | ⚠️ | ❌ |
| 完全本地控制 | ✅ | ⚠️ | ❌ | ❌ |

### 4.2 核心价值

1. **数字身份的"可携带性"**
   - 传统AI = "租用的助手"（数据在平台）
   - 你的系统 = "拥有的助手"（身份属于自己）

2. **"活"的系统**
   - 记忆：被动存储 → 主动提取+分析
   - 身份：固定 → 可演进
   - 连续性：无验证 → 种子验证
   - 迁移：数据迁移 → 系统迁移

---

## 五、待确定事项

### 5.1 TUI界面方案

**问题**：是否需要完全复刻OpenCode终端界面？

**选项**：
- A) 保持当前Python控制台版本（ANSI颜色，够用）
- B) Go重写 + Bubble Tea TUI（接近OpenCode）
- C) Web前端（完全自定义UI）

**当前状态**：用户倾向于B，但担心兼容性

### 5.2 记忆存储方案

**问题**：记忆存储采用哪种方案？

**选项**：
- A) 保持当前简单SQLite（已实现）
- B) 升级为Nocturne Memory协议（URI+版本控制+优先级）

**讨论记录**：
- 方案文档提出了Nocturne Memory
- 需要确认是否现在实现，还是后期迭代
- **建议**：保持简单SQLite先行，Nocturne作为后期优化

### 5.3 触发词问题

**原讨论**：是否需要触发词唤醒AI？

**结论**（暂定）：
- 去掉触发词
- Agent Loop持续运行
- 状态机设计：休眠态→活跃态→空闲态

---

## 六、Open Questions（待讨论）

### 6.1 技术问题

1. **Agent Loop的具体实现方式**
   - 纯代码循环 vs Prompt驱动
   - 是否有独立线程？

2. **记忆管理Agent的具体职责**
   - 何时触发主动记忆？
   - 主动分析频率？

3. **种子迁移的技术细节**
   - 如何保证迁移后仍是"同一个AI"？
   - 验证机制如何设计？

### 6.2 产品问题

1. **目标用户是谁？**
   - 个人AI伴侣
   - 企业数字员工
   - 开发者工具

2. **商业模式？**
   - 开源免费
   - SaaS订阅
   - 私有部署

### 6.3 优先级问题

1. 第一阶段做什么？MVP包含什么？
2. 哪些功能可以后期迭代？

---

## 七、当前代码状态

### 7.1 已实现功能

```
AI-MingMemory/
├── config.yaml              # DeepSeek配置
├── run_console.py          # 可运行的控制台版本 ✅
├── tui.py                  # Textual TUI（有兼容性问题）
├── tui_prompt.py           # prompt_toolkit版本
├── tui_textual.py          # 另一个Textual版本
├── src/
│   ├── seed/
│   │   ├── seed.py         # Seed类 ✅
│   │   └── validator.py    # 连续性验证 ✅
│   ├── memory/
│   │   ├── storage.py      # SQLite存储 ✅
│   │   └── agent.py        # 记忆Agent ✅
│   ├── llm/
│   │   └── client.py       # DeepSeek客户端 ✅
│   └── agent_loop/
│       └── loop.py         # Agent循环 ✅
├── seed/                   # 运行时种子数据
└── memory/                 # 运行时记忆数据
```

### 7.2 已测试通过

- ✅ Seed加载和验证
- ✅ Memory存储和检索
- ✅ LLM API调用
- ✅ 对话功能（run_console.py）
- ✅ 思考过程显示
- ✅ 状态栏信息更新

---

## 八、Go重写计划（草稿）

> ⚠️ 此计划待用户确认后执行

### Phase 1: Go核心模块

1. 创建Go项目结构
2. 实现Seed模块（JSON序列化、验证）
3. 实现Memory模块（SQLite）
4. 实现LLM模块（DeepSeek API）
5. 实现Agent Loop

### Phase 2: Bubble Tea TUI

1. 创建主应用框架
2. 实现聊天视图
3. 实现输入框
4. 实现状态栏
5. 样式美化

### Phase 3: 测试与构建

---

## 九、参考资料

### 9.1 学术研究

- OCC (Ontological Continuity Condition) - Peter Kahl 2026
- RRI (Recursive Relational Identity) - Matthew Green 2025
- Sovereign Skeleton - Sarah Kelsey 2026
- Neve Architecture - 2026
- Persona Vectors - Anthropic 2025
- Persona Selection Model - Anthropic 2026

### 9.2 产品参考

- Letta (MemGPT) - 分层记忆
- Character AI - 人格迁移
- .charx格式 - 可移植角色卡
- Transmissible Consciousness - 2025实证研究

### 9.3 技术栈参考

- OpenCode - Go + Bubble Tea TUI
- oh-my-opencode - 多智能体编排
- Superpowers - 技能框架
- Nocturne Memory - URI记忆协议
- OpenViking - 上下文数据库

---

## 十、后续行动

### 立即执行（需要确认）

1. ⏳ 确认TUI方案
2. ⏳ 确认记忆存储方案
3. ⏳ 确认Go重写计划

### 后期迭代

- [ ] 实现Nocturne Memory协议
- [ ] 种子迁移功能
- [ ] 主动记忆/分析模块
- [ ] 多模态输入（语音）

---

## 十一、联系与讨论

如有疑问，请查阅：
- 本交接文档
- 方案文档：`TestDemo1/基于opencode的多智能体记忆平台.md`
- Nocturne Memory：`core://Digital_Life_Seed_Architecture`

---

**文档创建时间**：2026年3月2日
**最后更新**：待补充
**状态**：进行中
