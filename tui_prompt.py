#!/usr/bin/env python3
import sys, os
if sys.platform == "win32":
    import codecs
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    except: pass

import asyncio
from datetime import datetime
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.widgets import Frame
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style

style = Style.from_dict({
    "window": "bg:#1e1e2e", "frame": "bg:#1e1e2e", "title": "fg:#cdd6f4 bold",
    "chat": "bg:#181825", "user": "fg:#89b4fa bold", "ai": "fg:#a6e3a1 bold",
    "system": "fg:#f9e2af", "status": "fg:#94e2d5", "seed": "fg:#f9e2af",
    "memory": "fg:#89b4fa", "thinking": "fg:#cba6f7",
    "input": "bg:#313244 fg:#cdd6f4", "separator": "fg:#45475a",
})

class ChatMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content
        self.timestamp = datetime.now().strftime("%H:%M")
    def to_formatted(self):
        if self.role == "user": return [("user", f"[{self.timestamp}] you: {self.content}" + chr(10))]
        elif self.role == "ai": return [("ai", f"[{self.timestamp}] AI: {self.content}" + chr(10))]
        else: return [("system", f"[{self.timestamp}] system: {self.content}" + chr(10))]

class MingMemoryApp:
    def __init__(self):
        self.messages = []
        self.status = "initializing..."
        self.seed_name = "not loaded"
        self.memory_count = 0
        self.thinking_steps = []
        self.current_thinking = ""
        self.is_processing = False
        self.seed = None
        self.memory_storage = None
        self.memory_agent = None
        self.llm_client = None
        self.chat_display = FormattedTextControl(text=self._build_chat())
        self.status_display = FormattedTextControl(text=self._build_status())
        self.input_buffer = Buffer(multiline=False, accept_handler=self._on_input)
        self.kb = KeyBindings()
        @self.kb.add("c-c", eager=True)
        @self.kb.add("c-q", eager=True)
        def exit_(e): e.app.exit()
        chat_window = Window(self.chat_display, style="chat", ignore_content_height=True)
        self.layout = Layout(HSplit([VSplit([Frame(chat_window, style="frame", width=3), Frame(Window(self.status_display, style="status"), style="frame", width=30)]), Frame(Window(self.input_buffer, style="input", width=80), style="frame", height=3)]))
        self.app = Application(layout=self.layout, key_bindings=self.kb, style=style, full_screen=True)

    def _build_chat(self):
        lines = [("title", chr(10) + "============================================================" + chr(10)), ("title", "              AI-MingMemory Digital Life" + chr(10)), ("title", "============================================================" + chr(10) + chr(10))]
        if not self.messages: lines.extend([("system", "  Type message and press enter to send" + chr(10)), ("system", "  Type quit or Ctrl+C to exit" + chr(10) + chr(10))])
        for m in self.messages: lines.extend(m.to_formatted())
        if self.current_thinking: lines.append(("thinking", chr(10) + "> Thinking: " + self.current_thinking + "..." + chr(10)))
        return lines

    def _build_status(self):
        lines = [("status", chr(10) + "-- Status --------------------------------" + chr(10) + "  " + self.status + chr(10) + chr(10)), ("seed", "-- Seed --------------------------------" + chr(10)), ("seed", "  " + self.seed_name + chr(10) + chr(10)), ("memory", "-- Memory ---" + chr(10)), ("memory", "  " + str(self.memory_count) + " items" + chr(10) + chr(10)), ("thinking", "-- Thinking Process --------------------" + chr(10))]
        if self.thinking_steps:
            for s in self.thinking_steps[-3:]: lines.append(("thinking", "  > " + s + chr(10)))
        else: lines.append(("status", "  waiting for input..." + chr(10)))
        return lines

    def _refresh(self):
        self.chat_display.text = self._build_chat()
        self.status_display.text = self._build_status()

    def _on_input(self):
        t = self.input_buffer.text.strip()
        if not t: return
        self.input_buffer.text = ""
        if t.lower() == "quit": self.app.exit(); return
        self.messages.append(ChatMessage("user", t))
        self._refresh()
        asyncio.create_task(self._ai_reply(t))

    async def _ai_reply(self, user_input):
        self.is_processing = True
        for step in ["loading context", "searching memory", "generating response"]:
            self.current_thinking = step
            self.thinking_steps.append(step)
            self._refresh()
            await asyncio.sleep(0.4)
        try: response = await self._get_ai_response(user_input)
        except Exception as e: response = "Error: " + str(e)
        self.current_thinking = ""
        self.thinking_steps = []
        self.memory_count += 1
        self.messages.append(ChatMessage("ai", response))
        self.is_processing = False
        self._refresh()

    def _get_ai_response(self, user_input):
        def sync_call():
            sp = self.seed.to_prompt()
            mc = self.memory_agent.search(user_input)
            msgs = [{"role": "system", "content": sp + chr(10) + chr(10) + "Related Memory:" + chr(10) + mc}, {"role": "user", "content": user_input}]
            r = self.llm_client.chat(msgs)
            self.memory_agent.save(user_input, r)
            return r
        return asyncio.to_thread(sync_call)

    async def run(self):
        try:
            self.status = "loading seed..."; self._refresh()
            from src.seed.seed import Seed
            from src.seed.validator import ContinuityValidator
            self.seed = Seed.load("./seed")
            v = ContinuityValidator(self.seed)
            valid, msg = v.validate()
            if not valid:
                self.messages.append(ChatMessage("system", "Seed validation failed: " + msg)); self._refresh(); return
            self.seed_name = self.seed.identity.name
            self.status = "loading memory..."; self._refresh()
            from src.memory.storage import MemoryStorage
            from src.memory.agent import MemoryAgent
            import yaml
            self.memory_storage = MemoryStorage("./memory")
            self.memory_count = self.memory_storage.count()
            self.status = "connecting LLM..."; self._refresh()
            with open("config.yaml") as f: config = yaml.safe_load(f)
            from src.llm.client import LLMClient
            self.llm_client = LLMClient.from_config({"llm": config["llm"]})
            await asyncio.to_thread(lambda: self.llm_client.chat([{"role": "user", "content": "hi"}]))
            self.memory_agent = MemoryAgent(self.memory_storage, self.llm_client)
            self.status = "ready"
            self.messages.append(ChatMessage("system", "OK: " + self.seed_name + " ready!"))
            self._refresh()
        except Exception as e:
            self.messages.append(ChatMessage("system", "Init failed: " + str(e))); self._refresh(); return
        await self.app.run_async()

def main():
    print("Starting AI-MingMemory TUI...")
    app = MingMemoryApp()
    asyncio.run(app.run())

if __name__ == "__main__": main()
