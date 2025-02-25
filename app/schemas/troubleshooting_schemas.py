from pydantic import BaseModel, Field, field_validator
from typing import List

# Troubleshooting Item

class RootCause(BaseModel):
    id: str = Field(..., description="Unique ID starting with 'rc-'")
    description: str = Field(..., description="Description of the root cause")
    factors: List[str] = Field(..., description="Factors contributing to the root cause")

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str):
        if not value.startswith("rc-"):
            raise ValueError("ID must start with 'rc-'")
        return value

class Solution(BaseModel):
    id: str = Field(..., description="Unique ID starting with 'so-'")
    steps: List[str] = Field(..., description="Steps to resolve the issue")
    prevention_tips: List[str]

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str):
        if not value.startswith("so-"):
            raise ValueError("ID must start with 'so-'")
        return value

class TroubleshootingItem(BaseModel):
    id: str = Field(..., description="Unique ID starting with 'ti-'")
    title: str = Field(..., description="Title of the troubleshooting item")
    description: str = Field(..., description="Description of the troubleshooting item")
    severity: str = Field(..., description="Severity of the troubleshooting item")
    symptoms: List[str] = Field(..., description="Symptoms of the troubleshooting item")
    root_cause: RootCause = Field(..., description="Root cause of the troubleshooting item")
    solution: Solution = Field(..., description="Solution for the troubleshooting item")

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str):
        if not value.startswith("ti-"):
            raise ValueError("ID must start with 'ti-'")
        return value