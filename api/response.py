from typing import List, Union, Dict, Any
from pydantic import BaseModel
    
class ProcessResponse(BaseModel):
    code: int = 200
    # The message can be:
    # - A list of strings (for error messages)
    # - A dictionary (for keyword extraction: {"primary_keywords": [...], "suggested_keywords": [...]})
    # - A list of dictionaries (for search results: [{"full_name": ..., ...}, ...])
    message: Union[List[str], Dict[str, List[str]], List[Dict[str, Any]], str]