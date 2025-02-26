from pydantic import BaseModel, Field
from typing import List

class Solution(BaseModel):
    id: str = Field(..., description="Unique ID starting with 'so-'")
    description: str = Field(..., description="Description of the solution")
    steps: List[str] = Field(..., description="Steps to resolve the issue")
    prevention_tips: List[str] = Field(..., description="Prevention tips for the solution")