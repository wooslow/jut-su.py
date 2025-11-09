from typing import TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .episode import Episode
    from .arc import Arc


class Season(BaseModel):
    number: int = Field(..., gt=0, description="Season number")
    episodes: list["Episode"] = Field(default_factory=list, description="List of episodes in the season")
    arcs: list["Arc"] = Field(default_factory=list, description="List of arcs in the season")
    title: str | None = Field(None, description="Season title")
    
    model_config = {
        "frozen": False,
        "validate_assignment": True,
    }
