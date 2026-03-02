"""
Agent Loop - 强制执行引擎
"""

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
        config: Dict[str, Any],
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

        print(f"✅ 种子验证通过: {self.seed.identity.name}")
        print(f"📋 种子UUID: {self.seed.uuid}")

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
            {"role": "user", "content": user_input},
        ]

        # Step 4: 调用LLM
        response = self.llm_client.chat(messages)

        # Step 5: 强制写入记忆
        self.memory_agent.save(user_input, response)

        return response

    def run_interactive(self):
        """交互式运行"""
        print(f"\n🤖 {self.seed.identity.name} 已启动 (输入 'quit' 退出)")
        print(f"📋 种子: {self.seed.uuid}")
        print(f"🧠 强制记忆: 开启")
        print("-" * 50)

        while True:
            try:
                user_input = input("\n👤 你: ").strip()
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break

            if user_input.lower() in ["quit", "exit", "退出", "q"]:
                print("👋 再见!")
                break

            if not user_input:
                continue

            try:
                response = self.process(user_input)
                print(f"\n🤖 AI: {response}")
            except Exception as e:
                print(f"\n❌ 错误: {e}")
