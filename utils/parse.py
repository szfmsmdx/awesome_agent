import json
import logging
from typing import List
import re

class BaseOutputParser():
    def parse_prompt_response(self, response: str) -> List[str]:
        matches = re.findall(r'$(.*?)$', response)
        return matches