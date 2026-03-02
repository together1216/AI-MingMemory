#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")

import os

os.environ["PYTHONIOENCODING"] = "utf-8"

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
    load_dotenv()
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def main():
    config_path = "config.yaml"

    if not Path(config_path).exists():
        print(f"Error: 配置文件不存在: {config_path}")
        return

    config = load_config(config_path)

    seed_path = config.get("system", {}).get("seed_path", "./seed")
    memory_path = config.get("system", {}).get("memory_path", "./memory")

    # 初始化或加载种子
    if not Path(seed_path).exists() or not (Path(seed_path) / "seed.json").exists():
        print("Creating new seed...")
        name = "AI-MingMemory"  # 默认名称
        seed = Seed.create_new(seed_path, name)
        print(f"Seed created: {seed.uuid}")
    else:
        print("Loading seed...")
        seed = Seed.load(seed_path)
        print(f"Seed loaded: {seed.uuid}")

    # 初始化记忆存储
    memory_storage = MemoryStorage(memory_path)
    print(f"Memories: {memory_storage.count()}")

    # 初始化LLM客户端
    print("Initializing LLM client...")
    llm_client = LLMClient.from_config({"llm": config["llm"]})

    # 测试LLM连接
    try:
        test_response = llm_client.chat([{"role": "user", "content": "你好"}])
        print(f"LLM connected: {test_response[:50]}...")
    except Exception as e:
        print(f"LLM connection failed: {e}")
        return

    # 初始化记忆管理Agent
    memory_agent = MemoryAgent(memory_storage, llm_client)

    # 初始化Agent Loop
    agent_loop = AgentLoop(seed, memory_agent, llm_client, config)

    # 启动交互
    print(f"\n{seed.identity.name} ready! Type 'quit' to exit.\n")
    agent_loop.run_interactive()


if __name__ == "__main__":
    main()
