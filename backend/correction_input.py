from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints

RequestId = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9-]{6,40}$")]


class Correction(BaseModel):
    """封存后按原事件编号补的更正，request_id 由谱务侧生成用于重试幂等。"""

    event: str = Field(pattern=r"^[A-Z0-9-]{2,20}$")
    request_id: RequestId
    sample: str = Field(pattern=r"^(fit|check)$")
    lead: float = Field(ge=0, le=30)
    hands_busy: bool
    missed: bool
