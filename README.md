# AI-MingMemory

数字生命系统 - 基于种子层的AI助手

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 复制配置
cp config.example.yaml config.yaml

# 3. 编辑配置（填入API Key）
# 设置环境变量 MINIMAX_API_KEY 或 QWEN_API_KEY

# 4. 初始化种子
python main.py --init-seed

# 5. 运行
python main.py
```

## 项目结构

```
AI-MingMemory/
├── src/
│   ├── agent_loop/    # Agent Loop核心
│   ├── seed/          # 种子层
│   ├── memory/        # 记忆系统
│   ├── llm/           # LLM客户端
│   └── terminal/      # 终端适配器
├── seed/              # 运行时种子目录
├── memory/            # 运行时记忆目录
├── config.yaml        # 配置文件
└── main.py           # 入口
```

## 配置

```yaml
llm:
  provider: "minimax"  # 或 "qwen"
  api_key: "${API_KEY}"
  base_url: "https://api.minimax.chat/v1"
  model: "abab6.5s-chat"

system:
  seed_path: "./seed"
  memory_path: "./memory"
  auto_backup: true
```
