from typing import List, Any
from pydantic import BaseModel
    
class ProcessResponse(BaseModel):
    code: int = 200
    message: List[Any] = []