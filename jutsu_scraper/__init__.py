"""
Jut.su Scraper - library for parsing data from jut.su website
"""

__version__ = "0.1.0"

from .client import JutsuClient
from .models import Anime, Episode, Season, Arc, Rating

__all__ = [
    "JutsuClient",
    "Anime",
    "Episode",
    "Season",
    "Arc",
    "Rating",
]

