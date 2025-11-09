from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, model_validator

if TYPE_CHECKING:
    from .episode import Episode
    from .season import Season
    from .rating import Rating


class Anime(BaseModel):
    title: str = Field(..., min_length=1, description="Anime title")
    original_title: str | None = Field(None, description="Original title")
    url: str = Field("", description="Page URL")
    poster_url: str | None = Field(None, description="Poster URL")
    description: str | None = Field(None, description="Anime description")
    genres: list[str] = Field(default_factory=list, description="List of genres")
    themes: list[str] = Field(default_factory=list, description="List of themes")
    years: list[int] = Field(default_factory=list, description="List of release years")
    year: int | None = Field(None, description="First release year (for backward compatibility)")
    age_rating: str | None = Field(None, description="Age rating")
    rating: "Rating | None" = Field(None, description="Rating information")
    status: str | None = Field(None, description="Anime status (e.g., 'онгоинг')")
    episodes: list["Episode"] = Field(default_factory=list, description="List of all episodes")
    seasons: list["Season"] = Field(default_factory=list, description="List of seasons")
    
    @model_validator(mode='after')
    def set_year_from_years(self) -> "Anime":
        """Set year from years list if not set"""
        if not self.year and self.years:
            self.year = min(self.years)
        return self
    
    @classmethod
    def from_html(cls, html: str | bytes, url: str = "") -> "Anime":
        """
        Parse anime data from HTML
        
        Args:
            html: HTML content (str or bytes)
            url: Page URL
            
        Returns:
            Parsed Anime object
        """
        from ..parser import parse_anime_html
        return parse_anime_html(html, url)
    
    def to_dict(self) -> dict:
        """
        Convert Anime object to dictionary (backward compatibility)
        
        Returns:
            Dictionary representation of Anime
        """
        data = self.model_dump(mode='python', exclude_none=False)
        
        if data.get("rating"):
            rating = data["rating"]
            data["rating"] = {
                "value": rating["value"],
                "best": rating["best"],
                "worst": rating["worst"],
                "count": rating["count"],
            }
        
        data["episodes"] = [
            {
                "number": ep["number"],
                "title": ep["title"],
                "url": ep["url"],
                "season_number": ep.get("season_number"),
            }
            for ep in data.get("episodes", [])
        ]
        
        if data.get("seasons"):
            data["seasons"] = [
                {
                    "number": season["number"],
                    "title": season.get("title"),
                    "episodes_count": len(season.get("episodes", [])),
                    "episodes": [
                        {
                            "number": ep["number"],
                            "title": ep["title"],
                            "url": ep["url"],
                        }
                        for ep in season.get("episodes", [])
                    ],
                    "arcs": [
                        {
                            "name": arc["name"],
                            "title": arc.get("title"),
                            "episodes_count": len(arc.get("episodes", [])),
                            "episodes": [
                                {
                                    "number": ep["number"],
                                    "title": ep["title"],
                                    "url": ep["url"],
                                }
                                for ep in arc.get("episodes", [])
                            ],
                        }
                        for arc in season.get("arcs", [])
                    ] if season.get("arcs") else None,
                }
                for season in data["seasons"]
            ]
        
        return data
    
    model_config = {
        "frozen": False,
        "validate_assignment": True,
        "arbitrary_types_allowed": False,
    }
