#!/usr/bin/env python3
"""
AI-MingMemory TUI - 集成核心逻辑
"""

import sys
import os

# Windows UTF-8
if sys.platform == "win32":
    import codecs

    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")
    except:
        pass

import asyncio
from datetime import datetime


# ANSI颜色
class ANSI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_BLACK = "\033[90m"


class TerminalUI:
    """终端UI"""

    def __init__(self, width: int = 70):
        self.width = width
        self.messages = []
        self.status = "初始化中..."
        self.seed_name = "未加载"
        self.memory_count = 0
        self.thinking_steps = []
        self.current_thinking = ""

        # 核心组件
        self.seed = None
        self.memory_storage = None
        self.memory_agent = None
        self.llm_client = None

    def clear(self):
        if os.name == "nt":
            os.system("cls")
        else:
            print("\033[2J\033[H", end="")

    def print_line(self, char="=", color=""):
        print(f"{color}{char * self.width}{ANSI.RESET}")

    def print_header(self):
        print()
        self.print_line("=", ANSI.BRIGHT_CYAN)
        title = " AI-MingMemory 数字生命 "
        padding = (self.width - len(title)) // 2
        print(f"{ANSI.BRIGHT_CYAN}{ANSI.BOLD}{' ' * padding}{title}{ANSI.RESET}")
        self.print_line("=", ANSI.BRIGHT_CYAN)
        print()

    def print_message(self, role, content, timestamp=None):
        ts = timestamp or datetime.now().strftime("%H:%M")

        if role == "user":
            prefix = f"{ANSI.BRIGHT_CYAN}[{ts}] 你:{ANSI.RESET}"
            color = ANSI.CYAN
        elif role == "ai":
            prefix = f"{ANSI.BRIGHT_GREEN}[{ts}] AI:{ANSI.RESET}"
            color = ANSI.GREEN
        else:
            prefix = f"{ANSI.BRIGHT_YELLOW}[{ts}] 系统:{ANSI.RESET}"
            color = ANSI.YELLOW

        print(f"\n{prefix}")

        max_width = self.width - 4
        words = content.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 <= max_width:
                line = (line + " " + word).strip() if line else word
            else:
                print(f"  {color}{line}{ANSI.RESET}")
                line = word
        if line:
            print(f"  {color}{line}{ANSI.RESET}")
        print()

    def print_sidebar(self):
        print(f"\n{ANSI.BRIGHT_BLACK}{'─' * self.width}{ANSI.RESET}")

        status_color = (
            ANSI.BRIGHT_GREEN if self.status == "就绪" else ANSI.BRIGHT_YELLOW
        )
        print(f"{status_color}状态:{ANSI.RESET} {self.status}")
        print(f"{ANSI.BRIGHT_YELLOW}种子:{ANSI.RESET} {self.seed_name}")
        print(f"{ANSI.BRIGHT_BLUE}记忆:{ANSI.RESET} {self.memory_count} 条")

        print(f"{ANSI.BRIGHT_MAGENTA}思考:{ANSI.RESET}")
        if self.thinking_steps:
            for step in self.thinking_steps[-3:]:
                print(f"  {ANSI.DIM}▸ {step}{ANSI.RESET}")
        else:
            print(f"  {ANSI.DIM}▸ 等待输入...{ANSI.RESET}")

        self.print_line("─", ANSI.BRIGHT_BLACK)

    def render(self):
        self.clear()
        self.print_header()

        for msg in self.messages:
            self.print_message(msg["role"], msg["content"], msg.get("timestamp"))

        if self.current_thinking:
            print(
                f"\n{ANSI.BRIGHT_MAGENTA}▸ 思考: {self.current_thinking}...{ANSI.RESET}"
            )

        self.print_sidebar()

        print(f"\n{ANSI.BRIGHT_GREEN}>> {ANSI.RESET}", end="", flush=True)

    def add_message(self, role, content):
        self.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().strftime("%H:%M"),
            }
        )


async def main():
    ui = TerminalUI()
    ui.render()

    # 初始化核心组件
    try:
        ui.status = "加载种子..."
        ui.render()

        from src.seed.seed import Seed
        from src.seed.validator import ContinuityValidator

        ui.seed = Seed.load("./seed")

        validator = ContinuityValidator(ui.seed)
        valid, msg = validator.validate()
        if not valid:
            ui.add_message("system", f"种子验证失败: {msg}")
            ui.render()
            return

        ui.seed_name = ui.seed.identity.name
        ui.status = "加载记忆..."
        ui.render()

        from src.memory.storage import MemoryStorage
        from src.memory.agent import MemoryAgent

        ui.memory_storage = MemoryStorage("./memory")
        ui.memory_count = ui.memory_storage.count()

        ui.status = "连接LLM..."
        ui.render()

        import yaml

        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        from src.llm.client import LLMClient

        ui.llm_client = LLMClient.from_config({"llm": config["llm"]})

        # 测试连接
        await asyncio.to_thread(
            lambda: ui.llm_client.chat([{"role": "user", "content": "hi"}])
        )

        ui.memory_agent = MemoryAgent(ui.memory_storage, ui.llm_client)

        ui.status = "就绪"
        ui.add_message("system", f"✓ {ui.seed_name} 准备就绪!")
        ui.render()

    except Exception as e:
        ui.add_message("system", f"初始化失败: {e}")
        ui.render()
        return

    # 主循环
    while True:
        try:
            user_input = input()

            if user_input.lower() in ["quit", "exit", "q"]:
                print(f"\n{ANSI.BRIGHT_GREEN}再见了！{ANSI.RESET}")
                break

            if not user_input.strip():
                ui.render()
                continue

            ui.add_message("user", user_input)
            ui.current_thinking = "思考中"
            ui.render()

            # 思考步骤
            steps = ["加载种子层", "搜索记忆", "生成回复"]
            for step in steps:
                ui.thinking_steps.append(step)
                ui.render()
                await asyncio.sleep(0.3)

            # AI回复
            def get_ai_response():
                seed_prompt = ui.seed.to_prompt()
                memory_context = ui.memory_agent.search(user_input)
                system_prompt = f"{seed_prompt}\n\n相关记忆:\n{memory_context}"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ]
                response = ui.llm_client.chat(messages)
                ui.memory_agent.save(user_input, response)
                return response

            try:
                response = await asyncio.to_thread(get_ai_response)
            except Exception as e:
                response = f"抱歉，出错了: {e}"

            ui.current_thinking = ""
            ui.thinking_steps = []
            ui.memory_count = ui.memory_storage.count()

            ui.add_message("ai", response)
            ui.render()

        except KeyboardInterrupt:
            print(f"\n\n{ANSI.BRIGHT_YELLOW}退出中...{ANSI.RESET}")
            break
        except Exception as e:
            print(f"\n{ANSI.BRIGHT_RED}错误: {e}{ANSI.RESET}")
            ui.render()


if __name__ == "__main__":
    print("启动 AI-MingMemory...")
    print("输入 quit 退出\n")
    asyncio.run(main())
