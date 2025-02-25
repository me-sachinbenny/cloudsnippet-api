from pydantic import BaseModel, Field,field_validator
from typing import Optional, List

# Implementation Guide
class ImplementationStep(BaseModel):
    id: str = Field(..., description="Unique ID starting with 'is-'")
    title: str
    code: str
    description: str
    image: Optional[str]

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str):
        if not value.startswith("is-"):
            raise ValueError("ID must start with 'is-'")
        return value


class ImplementationGuide(BaseModel):
    id: str = Field(..., description="Unique ID starting with 'ig-'")
    title: str
    description: str
    steps: Optional[List[ImplementationStep]]

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str):
        if not value.startswith("ig-"):
            raise ValueError("ID must start with 'ig-'")
        return value