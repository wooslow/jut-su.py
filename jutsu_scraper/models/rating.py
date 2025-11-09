from pydantic import BaseModel, Field, model_validator


class Rating(BaseModel):
    value: float = Field(..., description="Rating value")
    best: float = Field(10.0, description="Best possible rating")
    worst: float = Field(1.0, description="Worst possible rating")
    count: int = Field(..., ge=0, description="Number of ratings")
    
    @model_validator(mode='after')
    def validate_bounds(self) -> "Rating":
        """Validate rating value is within worst-best bounds"""
        if not (self.worst <= self.value <= self.best):
            raise ValueError(
                f"Rating value {self.value} must be between {self.worst} and {self.best}"
            )
        return self
    
    model_config = {
        "frozen": False,
        "validate_assignment": True,
    }
