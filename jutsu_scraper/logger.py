import logging
import sys
from typing import TextIO, BinaryIO
from io import TextIOWrapper


def setup_logger(
    name: str = "jutsu_scraper",
    level: int = logging.WARNING,
    format_string: str | None = None,
    stream: TextIO | BinaryIO | TextIOWrapper | None = None
) -> logging.Logger:
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        level: Logging level (default: WARNING)
        format_string: Custom format string for log messages
        stream: Output stream (default: sys.stderr)
        
    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if stream is None:
        stream = sys.stderr
    
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name (default: "jutsu_scraper")
        
    Returns:
        Logger instance
    """
    if name is None:
        name = "jutsu_scraper"
    
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        return setup_logger(name)
    
    return logger
