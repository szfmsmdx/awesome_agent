from pydantic import BaseModel
from typing import List

class InputRequest(BaseModel):
    text: str    
    
class KeyWordRequest(BaseModel):
    text: str
    max_results: int = 10