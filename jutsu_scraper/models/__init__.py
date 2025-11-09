from .episode import Episode
from .rating import Rating
from .arc import Arc
from .season import Season
from .anime import Anime

Episode.model_rebuild()
Arc.model_rebuild()
Season.model_rebuild()
Anime.model_rebuild()

__all__ = [
    "Episode",
    "Rating",
    "Arc",
    "Season",
    "Anime"
]

