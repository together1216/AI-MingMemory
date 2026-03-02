#!/usr/bin/env python3
import asyncio
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Input, Log
from textual import work
from textual.binding import Binding

class AI_MingMemory_TUI(App):
    CSS = """
    Screen { layout: grid; grid-size: 3 1; }
    #left { column-span: 2; }
    #right { width: 30; }
    #chat-area { height: 85%; border: solid blue; margin: 1; padding: 1; }
    #input-area { height: 5; border: solid green; margin: 1; padding: 1; }
    #status-panel { height: 100%; border: solid blue; margin: 1; padding: 1; }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.seed = None
        self.memory_storage = None
        self.memory_agent = None
        self.llm_client = None
        self.is_processing = False
        
    def compose(self) -> ComposeResult:
        with Vertical(id="left"):
            with Vertical(id="chat-area"):
                yield Log(id="chat", markup=True, auto_scroll=True)
            with Horizontal(id="input-area"):
                yield Input(placeholder="Type message... (Enter to send)", id="input")
        
        with Vertical(id="right"):
            with Vertical(id="status-panel"):
                yield Static("=" * 28)
                yield Static("Status")
                yield Static("Initializing...", id="status")
                yield Static("")
                yield Static("=" * 28)
                yield Static("Seed")
                yield Static("Not loaded", id="seed_info")
                yield Static("")
                yield Static("=" * 28)
                yield Static("Memory")
                yield Static("0 items", id="mem_count")
                yield Static("")
                yield Static("=" * 28)
                yield Static("Thinking")
                yield Static("Waiting...", id="thinking")
    
    async def on_mount(self):
        await self.init_components()
    
    async def init_components(self):
        try:
            self.append_log("system", "Initializing...")
            
            from src.seed.seed import Seed
            from src.seed.validator import ContinuityValidator
            from src.memory.storage import MemoryStorage
            from src.memory.agent import MemoryAgent
            from src.llm.client import LLMClient
            import yaml
            
            self.seed = Seed.load("./seed")
            validator = ContinuityValidator(self.seed)
            valid, msg = validator.validate()
            if not valid:
                self.append_log("system", f"Seed validation failed: {msg}")
                return
            
            self.memory_storage = MemoryStorage("./memory")
            
            with open("config.yaml") as f:
                config = yaml.safe_load(f)
            self.llm_client = LLMClient.from_config({"llm": config["llm"]})
            
            await asyncio.to_thread(lambda: self.llm_client.chat([{"role": "user", "content": "hi"}]))
            
            self.memory_agent = MemoryAgent(self.memory_storage, self.llm_client)
            
            self.query_one("#status", Static).update("Ready")
            self.query_one("#seed_info", Static).update(self.seed.identity.name)
            self.query_one("#mem_count", Static).update(str(self.memory_storage.count()) + " items")
            self.append_log("system", f"OK: {self.seed.identity.name} ready!")
            
        except Exception as e:
            self.append_log("system", f"Init failed: {e}")
    
    def append_log(self, role, content):
        ts = datetime.now().strftime("%H:%M")
        chat = self.query_one("#chat", Log)
        if role == "user":
            chat.write(f"[{ts}] You: {content}", scroll=True)
        elif role == "ai":
            chat.write(f"[{ts}] AI: {content}", scroll=True)
        else:
            chat.write(f"[{ts}] System: {content}", scroll=True)
    
    def action_quit(self):
        self.exit()
    
    def on_input_submitted(self, event):
        if self.is_processing or not event.value.strip():
            return
        user_input = event.value.strip()
        event.input.value = ""
        
        self.is_processing = True
        self.query_one("#status", Static).update("Working...")
        self.append_log("user", user_input)
        self.process_message(user_input)
    
    @work(exclusive=True)
    async def process_message(self, user_input):
        try:
            self.query_one("#thinking", Static).update("Loading context...")
            await asyncio.sleep(0.3)
            self.query_one("#thinking", Static).update("Searching memory...")
            await asyncio.sleep(0.3)
            self.query_one("#thinking", Static).update("Generating response...")
            
            def process():
                sp = self.seed.to_prompt()
                mc = self.memory_agent.search(user_input)
                system_msg = sp + chr(10) + chr(10) + "Related Memory:" + chr(10) + mc
                msgs = [{"role": "system", "content": system_msg}, {"role": "user", "content": user_input}]
                r = self.llm_client.chat(msgs)
                self.memory_agent.save(user_input, r)
                return r
            
            response = await asyncio.to_thread(process)
            
            self.query_one("#thinking", Static).update("Done!")
            self.append_log("ai", response)
            self.query_one("#mem_count", Static).update(str(self.memory_storage.count()) + " items")
            self.query_one("#status", Static).update("Ready")
            await asyncio.sleep(1)
            self.query_one("#thinking", Static).update("Waiting...")
            
        except Exception as e:
            self.append_log("system", f"Error: {e}")
            self.query_one("#status", Static).update("Error")
            self.query_one("#thinking", Static).update("Error!")
        finally:
            self.is_processing = False

def main():
    import yaml
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    app = AI_MingMemory_TUI(config)
    app.run()

if __name__ == "__main__":
    main()
