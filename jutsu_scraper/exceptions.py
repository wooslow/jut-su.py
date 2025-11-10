class JutsuError(Exception):
    """Base exception for all jut-su.py errors"""
    pass


class AuthenticationError(JutsuError):
    """Exception raised when authentication fails"""
    pass


class VideoExtractionError(JutsuError):
    """Exception raised when video URL extraction fails"""
    pass


class DownloadError(JutsuError):
    """Exception raised when video download fails"""
    pass


class NetworkError(JutsuError):
    """Exception raised when network request fails"""
    pass


class ParseError(JutsuError):
    """Exception raised when HTML parsing fails"""
    pass

