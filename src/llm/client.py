"""
LLM客户端 - 支持多种服务商
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List


class LLMClient:
    """LLM客户端基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get("provider", "minimax")
        # 优先从配置读取API Key，如果没有则从环境变量
        self.api_key = config.get("api_key") or os.getenv("MINIMAX_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = config.get("base_url", "https://api.minimax.chat/v1")
        self.model = config.get("model", "abab6.5s-chat")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求 - 子类实现"""
        raise NotImplementedError

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "LLMClient":
        """从配置创建客户端"""
        provider = config.get("llm", {}).get("provider", "minimax")

        if provider == "minimax":
            return MiniMaxClient(config.get("llm", {}))
        elif provider == "qwen":
            return QwenClient(config.get("llm", {}))
        elif provider == "deepseek":
            return DeepSeekClient(config.get("llm", {}))
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")


class MiniMaxClient(LLMClient):
    """MiniMax客户端"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.minimax.io/v1")
        self.model = config.get("model", "MiniMax-M2.5")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 转换消息格式
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})

        payload = {"model": self.model, "messages": formatted_messages, **kwargs}

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code != 200:
            raise Exception(
                f"MiniMax API调用失败: {response.status_code} - {response.text}"
            )

        result = response.json()

        if "choices" not in result or len(result["choices"]) == 0:
            raise Exception(f"无效的API响应: {result}")

        return result["choices"][0]["message"]["content"]


class QwenClient(LLMClient):
    """阿里Qwen客户端"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get(
            "base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = config.get("model", "qwen-plus")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        formatted_messages = []
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})

        payload = {"model": self.model, "messages": formatted_messages, **kwargs}

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code != 200:
            raise Exception(
                f"Qwen API调用失败: {response.status_code} - {response.text}"
            )

        result = response.json()

        if "choices" not in result or len(result["choices"]) == 0:
            raise Exception(f"无效的API响应: {result}")

        return result["choices"][0]["message"]["content"]


class DeepSeekClient(LLMClient):
    """DeepSeek客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.deepseek.com/v1")
        self.model = config.get("model", "deepseek-chat")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})
        
        payload = {"model": self.model, "messages": formatted_messages, **kwargs}
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"DeepSeek API调用失败: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if "choices" not in result or len(result["choices"]) == 0:
            raise Exception(f"无效的API响应: {result}")
        
        return result["choices"][0]["message"]["content"]
