#!/usr/bin/env python3
"""
AI-MingMemory TUI - 简洁版，类似OpenCode风格
"""

import os
import sys

# 设置UTF-8编码
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

import asyncio
from datetime import datetime


class SimpleTUI:
    """简单但好看的TUI，类似OpenCode"""

    def __init__(self):
        self.messages = []
        self.input_buffer = ""
        self.is_thinking = False
        self.thinking_text = ""

    def clear_screen(self):
        """清屏"""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self):
        """打印头部"""
        print("=" * 60)
        print("  AI-MingMemory 数字生命")
        print("  输入 'quit' 退出")
        print("=" * 60)
        print()

    def print_message(self, role: str, content: str):
        """打印消息"""
        ts = datetime.now().strftime("%H:%M")
        if role == "user":
            print(f"\n[{ts}] 你: {content}")
        elif role == "ai":
            print(f"\n[{ts}] AI: {content}")
        else:
            print(f"\n[{ts}] 系统: {content}")
        print()

    def print_thinking(self):
        """打印思考状态"""
        if self.is_thinking:
            print(f"\r[思考中] {self.thinking_text}...", end="", flush=True)

    def print_chat_history(self):
        """打印聊天历史"""
        self.clear_screen()
        self.print_header()

        for msg in self.messages:
            role, content = msg
            self.print_message(role, content)

        if self.is_thinking:
            self.print_thinking()

    async def get_input(self, prompt: str = ">> ") -> str:
        """获取输入"""
        try:
            return input(prompt)
        except EOFError:
            return "quit"


class SmartTUI:
    """智能TUI - 支持ANSI颜色和光标控制"""

    # ANSI颜色代码
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # 颜色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # 背景色
    BG_BLACK = "\033[40m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    def __init__(self):
        self.messages = []
        self.status = "初始化中..."
        self.seed_name = "未加载"
        self.memory_count = 0
        self.thinking_steps = []
        self.current_thinking = ""

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def print_status_bar(self):
        """打印状态栏 - 类似OpenCode的右侧信息"""
        # 计算布局
        width = 60
        lines = []

        # 头部
        lines.append(self.CYAN + "=" * width + self.RESET)
        lines.append(
            self.BOLD + self.CYAN + "  AI-MingMemory".center(width) + self.RESET
        )
        lines.append(self.CYAN + "=" * width + self.RESET)

        # 状态
        lines.append(f"{self.GREEN}状态:{self.RESET} {self.status}")

        # 种子
        lines.append(f"{self.YELLOW}种子:{self.RESET} {self.seed_name}")

        # 记忆
        lines.append(f"{self.BLUE}记忆:{self.RESET} {self.memory_count} 条")

        # 思考过程
        lines.append(f"{self.MAGENTA}思考:{self.RESET}")
        if self.thinking_steps:
            for step in self.thinking_steps[-3:]:
                lines.append(f"  {self.DIM}{step}{self.RESET}")
        else:
            lines.append(f"  {self.DIM}等待输入...{self.RESET}")

        lines.append(self.CYAN + "=" * width + self.RESET)

        return "\n".join(lines)

    def render(self):
        """渲染整个界面"""
        self.clear_screen()

        # 打印聊天历史
        for role, content in self.messages:
            ts = datetime.now().strftime("%H:%M")
            if role == "user":
                print(f"\n{self.CYAN}[{ts}] 你:{self.RESET}")
            elif role == "ai":
                print(f"\n{self.GREEN}[{ts}] AI:{self.RESET}")
            else:
                print(f"\n{self.YELLOW}[{ts}] 系统:{self.RESET}")

            # 内容处理 - 长文本换行
            words = content.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > 55:
                    print("  " + line)
                    line = word
                else:
                    if line:
                        line += " " + word
                    else:
                        line = word
            if line:
                print("  " + line)

        # 打印思考状态
        if self.current_thinking:
            print(f"\n{self.MAGENTA}[思考] {self.current_thinking}...{self.RESET}")

        # 打印分隔线
        print("\n" + self.CYAN + "=" * 60 + self.RESET)

        # 打印状态栏
        print(self.print_status_bar())


async def main():
    """主函数"""
    tui = SmartTUI()
    tui.render()

    # 模拟初始化
    tui.status = "就绪"
    tui.seed_name = "AI-MingMemory"
    tui.memory_count = 0
    tui.render()

    # 主循环
    while True:
        try:
            # 打印输入提示
            print(f"\n{self.GREEN}>> {self.RESET}", end="")
            user_input = input()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n再见了！")
                break

            if not user_input.strip():
                continue

            # 添加用户消息
            tui.messages.append(("user", user_input))
            tui.current_thinking = "思考中"
            tui.render()

            # 模拟思考过程
            tui.thinking_steps.append("加载上下文")
            tui.render()
            await asyncio.sleep(0.5)

            tui.thinking_steps.append("搜索记忆")
            tui.render()
            await asyncio.sleep(0.5)

            tui.thinking_steps.append("生成回复")
            tui.render()
            await asyncio.sleep(0.5)

            # 模拟AI回复
            tui.current_thinking = ""
            tui.thinking_steps = []
            tui.memory_count += 1

            responses = [
                "我明白了。你想要一个更好看的界面。",
                "让我想想... 这个想法很有趣！",
                "好的，我会记住这件事。",
                "我可以帮你做任何事情！",
            ]
            import random

            response = random.choice(responses)

            tui.messages.append(("ai", response))
            tui.render()

        except KeyboardInterrupt:
            print("\n\n退出中...")
            break
        except Exception as e:
            print(f"\n错误: {e}")


if __name__ == "__main__":
    # 定义self在main之前
    import asyncio

    # 修复main函数
    async def run_main():
        tui = SmartTUI()
        tui.render()

        # 模拟初始化
        tui.status = "就绪"
        tui.seed_name = "AI-MingMemory"
        tui.memory_count = 0
        tui.render()

        # 主循环
        while True:
            try:
                # 打印输入提示
                print(f"\n>> ", end="")
                user_input = input()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\n再见了！")
                    break

                if not user_input.strip():
                    continue

                # 添加用户消息
                tui.messages.append(("user", user_input))
                tui.current_thinking = "思考中"
                tui.render()

                # 模拟思考过程
                tui.thinking_steps.append("加载上下文")
                tui.render()
                await asyncio.sleep(0.5)

                tui.thinking_steps.append("搜索记忆")
                tui.render()
                await asyncio.sleep(0.5)

                tui.thinking_steps.append("生成回复")
                tui.render()
                await asyncio.sleep(0.5)

                # 模拟AI回复
                tui.current_thinking = ""
                tui.thinking_steps = []
                tui.memory_count += 1

                responses = [
                    "我明白了。你想要一个更好看的界面。",
                    "让我想想... 这个想法很有趣！",
                    "好的，我会记住这件事。",
                    "我可以帮你做任何事情！",
                ]
                import random

                response = random.choice(responses)

                tui.messages.append(("ai", response))
                tui.render()

            except KeyboardInterrupt:
                print("\n\n退出中...")
                break
            except Exception as e:
                print(f"\n错误: {e}")

    asyncio.run(run_main())
