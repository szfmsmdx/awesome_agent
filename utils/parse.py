import ast
from typing import List
import re

class BaseOutputParser():
    def parse_prompt_response(self, text: str) -> List[str]:
        pattern = r'\[.*?\]'
        raw_lists = re.findall(pattern, text)

        result = []
        for item in raw_lists:
            try:
                parsed = ast.literal_eval(item)
                if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
                    result.append(parsed)
            except (SyntaxError, ValueError):
                continue

        return result