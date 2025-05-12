import os
from utils.singleton import Singleton

class Config(metaclass=Singleton):
    def __init__(self) -> None:
        self.llm_model = "qwen-plus"
        self.temperature = 0.3
        self.api_key = "sk-2a711100ac31418aa4421e4bcae6fcff"
        self.llm_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.llm_max_tokens = 5000
        self.server_post = 7111
        self.host = "0.0.0.0"