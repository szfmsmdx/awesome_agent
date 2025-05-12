from pydantic import BaseModel

class InputRequest(BaseModel):
    text: str    