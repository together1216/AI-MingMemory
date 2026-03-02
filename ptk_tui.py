#!/usr/bin/env python3
"""
AI-MingMemory TUI - 使用prompt_toolkit
类似OpenCode风格的终端界面
"""

import os
import sys

# Windows UTF-8设置
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

import asyncio
from datetime import datetime
from prompt_toolkit import Application
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Label, TextArea, Frame
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application.current import get_app
from prompt_toolkit.auto_suggest import AutoSuggest
from prompt_toolkit.completion import WordCompleter


# 颜色样式
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # 前景色
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


class ChatMessage:
    def __init__(self, role: str, content: str, timestamp: str = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")

    def to_formatted(self):
        """转换为prompt_toolkit格式"""
        if self.role == "user":
            return [
                ("", "\n"),
                (Colors.BRIGHT_CYAN + Colors.BOLD, f"[{self.timestamp}] "),
                (Colors.BRIGHT_CYAN, f"你: "),
                ("", f"{self.content}\n"),
            ]
        elif self.role == "ai":
            return [
                ("", "\n"),
                (Colors.BRIGHT_GREEN + Colors.BOLD, f"[{self.timestamp}] "),
                (Colors.BRIGHT_GREEN, f"AI: "),
                ("", f"{self.content}\n"),
            ]
        else:  # system
            return [
                ("", "\n"),
                (Colors.BRIGHT_YELLOW + Colors.BOLD, f"[{self.timestamp}] "),
                (Colors.BRIGHT_YELLOW, f"系统: "),
                ("", f"{self.content}\n"),
            ]


class MingMemoryTUI:
    def __init__(self):
        self.messages = []
        self.status = "初始化中..."
        self.seed_name = "未加载"
        self.memory_count = 0
        self.thinking_steps = []
        self.current_thinking = ""

        # UI组件
        self.chat_display = FormattedTextControl(
            text=self._build_chat_text(),
            scrollable=True,
        )

        self.status_display = FormattedTextControl(
            text=self._build_status_text(),
        )

        self.input_area = TextArea(
            multiline=False,
            accept_handler=self._on_input_submit,
            get_line_prefix=self._get_input_prefix,
        )

        # 按键绑定
        self.kb = KeyBindings()

        @self.kb.add("c-c", eager=True)
        @self.kb.add("c-q", eager=True)
        def exit_app(event):
            """退出应用"""
            event.app.exit()

        # 布局
        self.root_container = VSplit(
            [
                # 左侧：聊天区域
                HSplit(
                    [
                        # 聊天消息显示
                        Window(self.chat_display, style="class:chat"),
                        # 输入框
                        Frame(
                            self.input_area,
                            style="class:input",
                        ),
                    ],
                    width=3,
                ),  # 占据3/4
                # 右侧：状态栏
                Window(
                    self.status_display,
                    style="class:status",
                    width=1,  # 占据1/4
                ),
            ]
        )

        self.layout = Layout(self.root_container)
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            full_screen=True,
        )

    def _build_chat_text(self):
        """构建聊天文本"""
        lines = []

        # 欢迎信息
        lines.extend(
            [
                ("", "\n"),
                (Colors.BRIGHT_CYAN + Colors.BOLD, "  AI-MingMemory 数字生命\n"),
                ("", "\n"),
                (Colors.BRIGHT_YELLOW, "  输入消息后按回车发送\n"),
                (Colors.BRIGHT_YELLOW, "  输入 quit 退出\n"),
                ("", "\n"),
                (Colors.BRIGHT_BLACK, "=" * 60 + "\n"),
                ("", "\n"),
            ]
        )

        # 聊天历史
        for msg in self.messages:
            lines.extend(msg.to_formatted())

        # 思考中
        if self.current_thinking:
            lines.extend(
                [
                    ("", "\n"),
                    (Colors.BRIGHT_MAGENTA, f"[思考] {self.current_thinking}...\n"),
                ]
            )

        return lines

    def _build_status_text(self):
        """构建状态文本"""
        lines = []

        lines.extend(
            [
                (Colors.BRIGHT_CYAN + Colors.BOLD, "\n" + "=" * 30 + "\n"),
                (Colors.BRIGHT_CYAN + Colors.BOLD, "  状态\n"),
                (Colors.BRIGHT_CYAN, "=" * 30 + "\n"),
                (Colors.BRIGHT_GREEN, f"{self.status}\n"),
                ("", "\n"),
                (Colors.BRIGHT_CYAN, "=" * 30 + "\n"),
                (Colors.BRIGHT_CYAN + Colors.BOLD, "  种子\n"),
                (Colors.BRIGHT_CYAN, "=" * 30 + "\n"),
                (Colors.BRIGHT_YELLOW, f"{self.seed_name}\n"),
                ("", "\n"),
                (Colors.BRIGHT_CYAN, "=" * 30 + "\n"),
                (Colors.BRIGHT_CYAN + Colors.BOLD, "  记忆\n"),
                (Colors.BRIGHT_CYAN, "=" * 30 + "\n"),
                (Colors.BRIGHT_BLUE, f"{self.memory_count} 条\n"),
                ("", "\n"),
                (Colors.BRIGHT_CYAN, "=" * 30 + "\n"),
                (Colors.BRIGHT_CYAN + Colors.BOLD, "  思考过程\n"),
                (Colors.BRIGHT_CYAN, "=" * 30 + "\n"),
            ]
        )

        if self.thinking_steps:
            for step in self.thinking_steps[-3:]:
                lines.extend(
                    [
                        (Colors.DIM, f"  {step}\n"),
                    ]
                )
        else:
            lines.extend(
                [
                    (Colors.DIM, "  等待输入...\n"),
                ]
            )

        lines.extend(
            [
                ("", "\n"),
                (Colors.BRIGHT_CYAN, "=" * 30 + "\n"),
            ]
        )

        return lines

    def _get_input_prefix(self, line_no, other):
        """输入框前缀"""
        return [("Class:input.prompt", ">> ")]

    def _on_input_submit(self):
        """处理输入提交"""
        text = self.input_area.text.strip()
        if not text:
            return

        # 清空输入
        self.input_area.text = ""

        if text.lower() == "quit":
            self.app.exit()
            return

        # 添加用户消息
        self.messages.append(ChatMessage("user", text))
        self._refresh()

        # 模拟AI回复
        asyncio.create_task(self._ai_response(text))

    async def _ai_response(self, user_input: str):
        """AI回复"""
        # 思考步骤
        steps = ["加载上下文", "搜索记忆", "生成回复"]

        for step in steps:
            self.current_thinking = step
            self.thinking_steps.append(step)
            self._refresh()
            await asyncio.sleep(0.5)

        # 生成回复
        self.current_thinking = ""
        self.thinking_steps = []
        self.memory_count += 1

        responses = [
            "我明白了。你想要一个更好看的界面。",
            "让我想想... 这个想法很有趣！",
            "好的，我会记住这件事。",
            "我可以帮你做任何事情！",
        ]
        import random

        response = random.choice(responses)

        self.messages.append(ChatMessage("ai", response))
        self._refresh()

    def _refresh(self):
        """刷新显示"""
        self.chat_display.text = self._build_chat_text()
        self.status_display.text = self._build_status_text()
        self.app.invalidate()

    async def run_async(self):
        """异步运行"""
        # 初始化
        self.status = "就绪"
        self.seed_name = "AI-MingMemory"
        self._refresh()

        # 运行
        await self.app.run_async()

    def run(self):
        """运行"""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            print("\n再见了！")


def main():
    """主函数"""
    print("启动 AI-MingMemory TUI...")
    tui = MingMemoryTUI()
    tui.run()


if __name__ == "__main__":
    main()
