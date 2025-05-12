from typing import List
from pydantic import BaseModel
    
class ProcessResponse(BaseModel):
    code: int = 200
    message: List[str] = []