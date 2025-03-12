import torch
import requests
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List

class BaseModel():
    """ 模型基类 """
    def __init__(self, path: str = '') -> None:
        self.path = path
    
    def load_model(self):
        pass

    def chat(self, prompt: str, history: List[dict]):
        pass

class GLMChat(BaseModel):
    """ chatGLM模型导入 """
    def __init__(self, path: str = '') -> None:
        super().__init__(path)
        self.load_model()  # 初始化基类时进行模型导入
    
    def load_model(self):
        print("==================== Loading GLM model ====================")
        self.tokenizer = AutoTokenizer.from_pretrained(self.path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(self.path, torch_dtype=torch.float16, temperature=0.1, trust_remote_code=True).cuda().eval()
        print("==================== GLM Model loaded. ====================")
    
    def chat(self, prompt: str, history: List[dict]):
        response, history = self.model.chat(self.tokenizer, prompt, history)
        return response, history

class DeepSeekChat(BaseModel):
    """ DeepSeek-R1 API 调用 """
    def __init__(self, api_key: str, endpoint: str = "https://api.deepseek.com/v1/chat") -> None:
        super().__init__()
        self.api_key = api_key
        self.endpoint = endpoint

    def chat(self, prompt: str, history: List[dict]):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-r1",
            "messages": history + [{"role": "user", "content": prompt}],
        }
        response = requests.post(self.endpoint, json=payload, headers=headers)
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", ""), history

class GPT4oChat(BaseModel):
    """ GPT-4o API 调用 """
    def __init__(self, api_key: str, endpoint: str = "https://api.openai.com/v1/chat/completions") -> None:
        super().__init__()
        self.api_key = api_key
        self.endpoint = endpoint

    def chat(self, prompt: str, history: List[dict]):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o",
            "messages": history + [{"role": "user", "content": prompt}],
        }
        response = requests.post(self.endpoint, json=payload, headers=headers)
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", ""), history

class QwenChat(BaseModel):
    """ Qwen2.5 模型导入 """
    def __init__(self, path: str = '') -> None:
        super().__init__(path)
        self.load_model()

    def load_model(self):
        print("==================== Loading Qwen2.5 model ====================")
        self.tokenizer = AutoTokenizer.from_pretrained(self.path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.path, torch_dtype=torch.float16, trust_remote_code=True
        ).cuda().eval()
        print("==================== Qwen2.5 Model loaded. ====================")

    def chat(self, prompt: str, history: List[dict]):
        response, history = self.model.chat(self.tokenizer, prompt, history)
        return response, history

class LlamaChat(BaseModel):
    """ Llama3.1 模型导入 """
    def __init__(self, path: str = '') -> None:
        super().__init__(path)
        self.load_model()

    def load_model(self):
        print("==================== Loading Llama3.1 model ====================")
        self.tokenizer = AutoTokenizer.from_pretrained(self.path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.path, torch_dtype=torch.float16, trust_remote_code=True
        ).cuda().eval()
        print("==================== Llama3.1 Model loaded. ====================")

    def chat(self, prompt: str, history: List[dict]):
        response, history = self.model.chat(self.tokenizer, prompt, history)
        return response, history

