#!/usr/bin/env python3
"""
AI-MingMemory TUI - 纯Python标准库，兼容所有终端
"""

import sys
import os

# Windows UTF-8
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "write")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "write")

import asyncio
from datetime import datetime


# ANSI颜色 (仅在支持的终端启用)
class ANSI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # 亮色
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # 背景
    BG_BLACK = "\033[40m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"

    # 光标
    CURSOR_UP = "\033[A"
    CURSOR_DOWN = "\033[B"
    CLEAR_LINE = "\033[2K"
    CLEAR_SCREEN = "\033[2J"
    HOME = "\033[H"


class TerminalUI:
    """终端UI - 简洁类似OpenCode"""

    def __init__(self, width: int = 70):
        self.width = width
        self.messages = []
        self.status = "初始化中..."
        self.seed_name = "未加载"
        self.memory_count = 0
        self.thinking_steps = []
        self.current_thinking = ""

    def clear(self):
        """清屏"""
        if os.name == "nt":
            os.system("cls")
        else:
            print(ANSI.CLEAR_SCREEN + ANSI.HOME, end="")

    def print_line(self, char: str = "=", color: str = ""):
        """打印分隔线"""
        print(f"{color}{char * self.width}{ANSI.RESET}")

    def print_header(self):
        """打印头部"""
        print()
        self.print_line("=", ANSI.BRIGHT_CYAN)
        title = " AI-MingMemory 数字生命 "
        padding = (self.width - len(title)) // 2
        print(f"{ANSI.BRIGHT_CYAN}{ANSI.BOLD}{' ' * padding}{title}{ANSI.RESET}")
        self.print_line("=", ANSI.BRIGHT_CYAN)
        print()

    def print_message(self, role: str, content: str, timestamp: str = None):
        """打印消息"""
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

        # 文本换行处理
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
        """打印右侧状态栏"""
        # 分隔线
        print(f"\n{ANSI.BRIGHT_BLACK}{'─' * self.width}{ANSI.RESET}")

        # 状态
        status_color = (
            ANSI.BRIGHT_GREEN if self.status == "就绪" else ANSI.BRIGHT_YELLOW
        )
        print(f"{status_color}状态:{ANSI.RESET} {self.status}")

        # 种子
        print(f"{ANSI.BRIGHT_YELLOW}种子:{ANSI.RESET} {self.seed_name}")

        # 记忆
        print(f"{ANSI.BRIGHT_BLUE}记忆:{ANSI.RESET} {self.memory_count} 条")

        # 思考
        print(f"{ANSI.BRIGHT_MAGENTA}思考:{ANSI.RESET}")
        if self.thinking_steps:
            for step in self.thinking_steps[-3:]:
                print(f"  {ANSI.DIM}▸ {step}{ANSI.RESET}")
        else:
            print(f"  {ANSI.DIM}▸ 等待输入...{ANSI.RESET}")

        # 底部
        self.print_line("─", ANSI.BRIGHT_BLACK)

    def render(self):
        """渲染整个界面"""
        self.clear()
        self.print_header()

        # 聊天历史
        for msg in self.messages:
            self.print_message(msg["role"], msg["content"], msg.get("timestamp"))

        # 思考中
        if self.current_thinking:
            print(
                f"\n{ANSI.BRIGHT_MAGENTA}▸ 思考: {self.current_thinking}...{ANSI.RESET}"
            )

        # 状态栏
        self.print_sidebar()

        # 输入提示
        print(f"\n{ANSI.BRIGHT_GREEN}>> {ANSI.RESET}", end="", flush=True)

    def add_message(self, role: str, content: str):
        """添加消息"""
        self.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().strftime("%H:%M"),
            }
        )


async def main():
    """主函数"""
    ui = TerminalUI()
    ui.render()

    # 模拟初始化
    await asyncio.sleep(0.5)
    ui.status = "就绪"
    ui.seed_name = "AI-MingMemory"
    ui.render()

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

            # 添加用户消息
            ui.add_message("user", user_input)
            ui.current_thinking = "思考中"
            ui.render()

            # 思考步骤
            steps = ["加载上下文", "搜索记忆", "生成回复"]
            for step in steps:
                ui.thinking_steps.append(step)
                ui.render()
                await asyncio.sleep(0.4)

            # 清除思考状态
            ui.current_thinking = ""
            ui.thinking_steps = []
            ui.memory_count += 1

            # AI回复
            responses = [
                "你好！我是AI-MingMemory，你的数字生命助手。",
                "明白了，让我思考一下...",
                "这是一个很有趣的问题！",
                "我可以帮你记住事情，陪你聊天！",
            ]
            import random

            response = random.choice(responses)

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
