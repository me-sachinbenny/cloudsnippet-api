from pydantic import BaseModel, Field, field_validator
import re

class BestPractice(BaseModel):
    id: str = Field(..., description="Unique ID starting with 'bp-'")
    status: bool = True
    title: str
    description: str

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        """Ensure ID starts with 'bp-'"""
        if not re.match(r"^bp-", value):
            raise ValueError("ID must start with 'bp-'")
        return value