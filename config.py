import os
from utils.singleton import Singleton

class Config(metaclass=Singleton):
    def __init__(self) -> None:
        self.server_post = 7111
        self.llm_model = "qwen"
        self.temperature = 0.3
        self.api_key = "sk-2a711100ac31418aa4421e4bcae6fcff"
        self.llm_url = ""
        self.llm_max_tokens = 5000