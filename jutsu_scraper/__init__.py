"""
Jut.su Scraper - library for parsing data from jut.su website
"""

__version__ = "0.1.0"

from .client import JutsuClient
from .models import Anime, Episode, Season, Arc, Rating
from .exceptions import (
    JutsuError,
    AuthenticationError,
    VideoExtractionError,
    DownloadError,
    NetworkError,
    ParseError
)
from .logger import setup_logger, get_logger

__all__ = [
    "JutsuClient",
    "Anime",
    "Episode",
    "Season",
    "Arc",
    "Rating",
    "JutsuError",
    "AuthenticationError",
    "VideoExtractionError",
    "DownloadError",
    "NetworkError",
    "ParseError",
    "setup_logger",
    "get_logger",
]

