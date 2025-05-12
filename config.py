import os
from utils.singleton import Singleton

class Config(metaclass=Singleton):
    def __init__(self) -> None:
        self.server_post = 7111
        self.llm_model = "qwen"
        self.temperature = 0.3
        self.api_key = "API-KEY"
        self.llm_url = "LLM_URL"
        self.llm_max_tokens = 5000
