from pydantic import BaseModel, Field
from typing import List

class RootCause(BaseModel):
    id: str = Field(..., description="Unique ID starting with 'rc-'")
    description: str = Field(..., description="Description of the root cause")
    factors: List[str] = Field(..., description="Factors contributing to the root cause")