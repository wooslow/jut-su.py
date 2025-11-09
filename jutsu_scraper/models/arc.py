from pydantic import BaseModel, Field

from .episode import Episode


class Arc(BaseModel):
    name: str = Field(..., min_length=1, description="Arc name")
    episodes: list[Episode] = Field(default_factory=list, description="List of episodes in the arc")
    title: str | None = Field(None, description="English title of the arc")
    
    model_config = {
        "frozen": False,
        "validate_assignment": True,
    }
