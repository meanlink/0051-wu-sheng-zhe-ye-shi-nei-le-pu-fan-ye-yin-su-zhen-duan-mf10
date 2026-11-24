from typing import Literal
from pydantic import BaseModel,Field

class Turn(BaseModel):
    event:str=Field(pattern=r"^[A-Z0-9-]{2,20}$")
    sample:Literal['fit','check']
    lead:float=Field(ge=0,le=30)
    hands_busy:bool
    missed:bool
