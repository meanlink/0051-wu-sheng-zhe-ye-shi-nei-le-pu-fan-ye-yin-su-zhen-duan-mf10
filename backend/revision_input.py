from typing import Annotated
from pydantic import BaseModel,Field,StringConstraints

Slug=Annotated[str,StringConstraints(pattern=r"^[A-Z0-9-]{2,18}$")]

class Revision(BaseModel):
    code:Slug
    target_page:int=Field(ge=2,le=200)
    lead:float=Field(ge=0,le=30)
    hands_busy:bool
    trial_passes:int=Field(ge=0,le=3)

class Release(BaseModel):
    revision:Slug
    programme:Annotated[str,StringConstraints(strip_whitespace=True,min_length=5,max_length=100)]
