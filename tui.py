"""
AI-MingMemory TUI - 终端用户界面
"""

import asyncio
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Input, RichLog
from textual import work


class AI_MingMemory_TUI(App):
    CSS = """
    Screen { layout: grid; grid-size: 3 1; }
    #left { column-span: 2; }
    #right { width: 28%; }
    #chat { height: 75vh; border: solid blue; margin: 1; padding: 1; }
    #input_box { height: 3; border: solid green; margin: 1; padding: 1; }
    #status_panel { height: 100%; border: solid blue; margin: 1; padding: 1; }
    """

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.seed = None
        self.memory_storage = None
        self.memory_agent = None
        self.llm_client = None
        self.is_processing = False
        self.thinking_steps = []  # Store thinking steps
        self.queue = []  # Message queue

    def compose(self) -> ComposeResult:
        with Vertical(id="left"):
            yield RichLog(id="chat", markup=True)
            with Horizontal(id="input_box"):
                yield Input(placeholder="Enter message... (Press Enter)", id="input")

        with Vertical(id="right"):
            with Vertical(id="status_panel"):
                yield Static("=" * 22)
                yield Static("[b]状态 Status[/b]")
                yield Static("初始化中...", id="status")
                yield Static("")
                yield Static("=" * 22)
                yield Static("[b]种子 Seed[/b]")
                yield Static("未加载", id="seed_info")
                yield Static("")
                yield Static("=" * 22)
                yield Static("[b]记忆 Memory[/b]")
                yield Static("0 条", id="mem_count")
                yield Static("")
                yield Static("=" * 22)
                yield Static("[b]思考过程 Thinking[/b]")
                yield Static("等待中...", id="thinking")
                yield Static("")
                yield Static("=" * 22)
                yield Static("[b]队列 Queue[/b]")
                yield Static("空", id="queue_info")

    async def on_mount(self) -> None:
        await self.init_components()

    async def init_components(self):
        try:
            from src.seed.seed import Seed
            from src.seed.validator import ContinuityValidator
            from src.memory.storage import MemoryStorage
            from src.memory.agent import MemoryAgent
            from src.llm.client import LLMClient

            self.update_thinking("加载种子层...")
            self.update_status("初始化")

            seed_path = self.config.get("system", {}).get("seed_path", "./seed")
            self.seed = Seed.load(seed_path)

            validator = ContinuityValidator(self.seed)
            valid, msg = validator.validate()
            if not valid:
                self.log_error(f"Seed validation failed: {msg}")
                return

            self.update_thinking("验证种子完整性...")
            self.update_status("加载记忆")

            memory_path = self.config.get("system", {}).get("memory_path", "./memory")
            self.memory_storage = MemoryStorage(memory_path)

            self.update_thinking("连接 LLM...")
            self.update_status("连接API")
            self.llm_client = LLMClient.from_config({"llm": self.config["llm"]})

            # Test LLM connection
            await asyncio.to_thread(
                lambda: self.llm_client.chat([{"role": "user", "content": "hi"}])
            )

            self.memory_agent = MemoryAgent(self.memory_storage, self.llm_client)

            self.query_one("#status", Static).update("就绪 Ready")
            self.query_one("#seed_info", Static).update(f"{self.seed.identity.name}")
            self.query_one("#mem_count", Static).update(
                f"{self.memory_storage.count()} 条"
            )
            self.update_thinking("等待输入...")

            self.log_msg("system", f"✓ {self.seed.identity.name} 准备就绪!")

        except Exception as e:
            self.log_error(f"Init failed: {e}")

    def log_msg(self, role: str, content: str):
        chat = self.query_one("#chat")
        ts = datetime.now().strftime("%H:%M")
        if role == "user":
            chat.write(f"\n[{ts}] 你 YOU: {content}")
        elif role == "ai":
            chat.write(f"\n[{ts}] AI: {content}")
        else:
            chat.write(f"\n[{ts}] 系统: {content}")

    def log_error(self, content: str):
        self.log_msg("system", content)
        try:
            self.update_status("错误")
        except:
            pass

    def update_thinking(self, text: str):
        """Update thinking process display"""
        try:
            # Add timestamp to thinking step
            ts = datetime.now().strftime("%H:%M:%S")
            step = f"[{ts}] {text}"

            # Keep last 3 steps
            self.thinking_steps.append(step)
            if len(self.thinking_steps) > 3:
                self.thinking_steps.pop(0)

            # Display all steps
            display_text = "\n".join(self.thinking_steps)
            self.query_one("#thinking", Static).update(display_text)
        except:
            pass

    def update_status(self, text: str):
        """Update status display"""
        try:
            self.query_one("#status", Static).update(text)
        except:
            pass

    def update_queue_info(self):
        """Update queue display"""
        try:
            if self.queue:
                queue_text = f"{len(self.queue)} 条待处理"
                for i, msg in enumerate(self.queue[:3], 1):
                    queue_text += f"\n{i}. {msg[:20]}..."
            else:
                queue_text = "空"
            self.query_one("#queue_info", Static).update(queue_text)
        except:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.is_processing or not event.value.strip():
            return
        user_input = event.value.strip()
        event.input.value = ""

        # Add to queue
        self.queue.append(user_input)
        self.update_queue_info()

        self.is_processing = True
        self.update_status("工作中...")
        self.log_msg("user", user_input)
        self.process_message(user_input)

    @work(exclusive=True)
    async def process_message(self, user_input: str):
        try:
            # Step 1: Load seed
            self.update_thinking("加载种子层...")
            await asyncio.sleep(0.2)

            # Step 2: Search memory
            self.update_thinking("搜索记忆...")
            await asyncio.sleep(0.2)

            # Step 3: Generate response
            self.update_thinking("思考中...")

            def process():
                seed_prompt = self.seed.to_prompt()
                memory_context = self.memory_agent.search(user_input)
                system_prompt = f"{seed_prompt}\n\n相关记忆:\n{memory_context}"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ]
                response = self.llm_client.chat(messages)
                self.memory_agent.save(user_input, response)
                return response

            response = await asyncio.to_thread(process)

            # Step 4: Save to memory
            self.update_thinking("保存记忆...")
            await asyncio.sleep(0.1)

            # Done
            self.update_thinking("完成!")
            self.log_msg("ai", response)

            # Update memory count
            self.query_one("#mem_count", Static).update(
                f"{self.memory_storage.count()} 条"
            )

            self.update_status("就绪")
            await asyncio.sleep(1.5)
            self.update_thinking("等待输入...")

        except Exception as e:
            self.log_error(f"Error: {e}")
            self.update_status("错误")
            self.update_thinking("出错!")
        finally:
            # Remove from queue
            if user_input in self.queue:
                self.queue.remove(user_input)
            self.update_queue_info()
            self.is_processing = False


def main():
    import yaml

    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    app = AI_MingMemory_TUI(config)
    app.run()


if __name__ == "__main__":
    main()
