import os
from utils.singleton import Singleton

class Config(metaclass=Singleton):
    def __init__(self) -> None:
        self.llm_model = "qwen-plus"
        self.temperature = 0.3
        self.api_key = "API_KEY"
        self.llm_url = "LLM_URL"
        self.llm_max_tokens = 5000
        self.server_post = 7111
        self.host = "0.0.0.0"