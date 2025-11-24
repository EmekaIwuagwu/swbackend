from pydantic import BaseModel

class Resolution(BaseModel):
    width: int
    height: int
