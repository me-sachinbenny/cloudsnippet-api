from pydantic import BaseModel, Field

class ToolProjection(BaseModel):
    id: str
    name: str
    description: str = Field(default="")
    slug: str = Field(default="")
    image: str = Field(default="")

    model_config = {
        "validate_assignment": True,
        "extra": "ignore"
    }