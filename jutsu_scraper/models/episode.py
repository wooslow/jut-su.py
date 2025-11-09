from pydantic import BaseModel, Field, field_validator


class Episode(BaseModel):
    number: int = Field(..., gt=0, description="Episode number (must be positive)")
    title: str = Field(..., min_length=1, description="Episode title")
    url: str = Field(..., min_length=1, description="Episode URL")
    season_number: int | None = Field(None, gt=0, description="Season number if applicable")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL is not empty"""
        if not v or not v.strip():
            raise ValueError("Episode URL cannot be empty")
        return v.strip()
    
    model_config = {
        "frozen": False,
        "validate_assignment": True,
    }
