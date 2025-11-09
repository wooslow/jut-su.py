from typing import Optional
import requests
from fake_useragent import UserAgent

from .models.anime import Anime
from .constants import BASE_URL, DEFAULT_ENCODING


_ua = UserAgent()


def _get_default_headers() -> dict[str, str]:
    """
    Generate default HTTP headers with random User-Agent
    
    Returns:
        Dictionary of default headers
    """
    try:
        user_agent = _ua.random
    except Exception:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    return {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }


class JutsuClient:
    """Client for parsing data from jut.su website"""
    
    BASE_URL = BASE_URL
    
    def __init__(self, timeout: int = 10, headers: Optional[dict[str, str]] = None, use_random_ua: bool = True):
        """
        Initialize client
        
        Args:
            timeout: Request timeout in seconds
            headers: Additional HTTP headers (merged with defaults)
            use_random_ua: Whether to use random User-Agent for each request (default: True)
        """
        self.timeout = timeout
        self.use_random_ua = use_random_ua
        self.session = requests.Session()
        
        default_headers = _get_default_headers()
        if headers:
            default_headers.update(headers)
        
        self.session.headers.update(default_headers)
    
    def _get_html(self, url: str) -> Optional[str]:
        """
        Get HTML content from URL
        
        Args:
            url: Page URL
            
        Returns:
            HTML content or None on error
        """
        try:
            # Update User-Agent for each request if enabled
            if self.use_random_ua:
                try:
                    self.session.headers["User-Agent"] = _ua.random
                except Exception:
                    pass  # Keep existing User-Agent if update fails
            
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = DEFAULT_ENCODING
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error requesting {url}: {e}")
            return None
    
    def get_anime(self, anime_slug: str) -> Optional[Anime]:
        """
        Get anime information by slug
        
        Args:
            anime_slug: Anime slug (e.g., 'mayoiga')
            
        Returns:
            Anime object or None on error
        """
        url = f"{self.BASE_URL}/{anime_slug}/"
        html = self._get_html(url)
        
        if not html:
            return None
        
        return Anime.from_html(html, url)
    
    def get_anime_by_url(self, url: str) -> Optional[Anime]:
        """
        Get anime information by full URL
        
        Args:
            url: Full anime page URL
            
        Returns:
            Anime object or None on error
        """
        html = self._get_html(url)
        
        if not html:
            return None
        
        return Anime.from_html(html, url)
