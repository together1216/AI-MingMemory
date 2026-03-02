"""
AI-MingMemory 主入口
"""

import argparse
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

from src.seed.seed import Seed
from src.seed.validator import ContinuityValidator
from src.memory.storage import MemoryStorage
from src.memory.agent import MemoryAgent
from src.llm.client import LLMClient
from src.agent_loop.loop import AgentLoop


def load_config(config_path: str) -> dict:
    """加载配置"""
    # 加载.env文件
    load_dotenv()

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 处理环境变量
    if "api_key" in config.get("llm", {}):
        api_key = config["llm"]["api_key"]
        if api_key.startswith("${") and api_key.endswith("}"):
            env_var = api_key[2:-1]
            config["llm"]["api_key"] = os.getenv(env_var)

    return config


def main():
    parser = argparse.ArgumentParser(description="AI-MingMemory 数字生命系统")
    parser.add_argument("--config", default="config.yaml", help="配置文件")
    parser.add_argument("--init-seed", action="store_true", help="初始化种子")
    args = parser.parse_args()

    # 加载配置
    if not Path(args.config).exists():
        print(f"❌ 配置文件不存在: {args.config}")
        print("请复制 config.example.yaml 为 config.yaml 并编辑")
        return

    config = load_config(args.config)

    seed_path = config.get("system", {}).get("seed_path", "./seed")
    memory_path = config.get("system", {}).get("memory_path", "./memory")

    # 初始化或加载种子
    if args.init_seed or not Path(seed_path).exists():
        print("📦 创建新种子...")
        name = input("请输入AI名称 (默认: AI-MingMemory): ").strip()
        if not name:
            name = "AI-MingMemory"
        seed = Seed.create_new(seed_path, name)
        print(f"✅ 种子已创建: {seed.uuid}")
    else:
        print("📂 加载种子...")
        seed = Seed.load(seed_path)
        print(f"✅ 种子已加载: {seed.uuid}")

    # 初始化记忆存储
    memory_storage = MemoryStorage(memory_path)
    print(f"📚 记忆数量: {memory_storage.count()}")

    # 初始化LLM客户端
    print("🔗 初始化LLM客户端...")
    llm_client = LLMClient.from_config({"llm": config["llm"]})

    # 测试LLM连接
    try:
        test_response = llm_client.chat([{"role": "user", "content": "你好"}])
        print("✅ LLM连接成功")
    except Exception as e:
        print(f"❌ LLM连接失败: {e}")
        print("请检查API Key是否正确")
        return

    # 初始化记忆管理Agent
    memory_agent = MemoryAgent(memory_storage, llm_client)

    # 初始化Agent Loop
    agent_loop = AgentLoop(seed, memory_agent, llm_client, config)

    # 启动
    print(f"\n🚀 {seed.identity.name} 启动完成!\n")
    agent_loop.run_interactive()


if __name__ == "__main__":
    main()
