"""
Video URL extraction from episode pages
"""
import re
from bs4 import BeautifulSoup

from .logger import get_logger
from .exceptions import VideoExtractionError
from .constants import REGEX_QUALITY_FROM_LABEL, REGEX_QUALITY_FROM_URL, VIDEO_QUALITIES

logger = get_logger(__name__)


class VideoExtractor:
    """Extract video URLs from episode HTML pages"""
    
    @staticmethod
    def extract_from_source_tags(soup: BeautifulSoup) -> dict[str, str]:
        """
        Extract video URLs from <source> tags
        
        Args:
            soup: BeautifulSoup object of the HTML page
            
        Returns:
            Dictionary with quality as key and video URL as value
        """
        video_urls = {}
        source_tags = soup.find_all('source', type='video/mp4')
        
        for source in source_tags:
            src = source.get('src', '')
            if not src or '.mp4' not in src:
                continue
            
            quality = source.get('res', '')
            if not quality:
                label = source.get('label', '')
                if label:
                    quality_match = re.search(REGEX_QUALITY_FROM_LABEL, label)
                    if quality_match:
                        quality = quality_match.group(1)
            
            if quality and src:
                src = src.replace('&amp;', '&')
                video_urls[quality] = src
                logger.debug(f"Extracted {quality}p from <source> tag: {src[:80]}...")
        
        return video_urls
    
    @staticmethod
    def extract_from_video_tag(soup: BeautifulSoup) -> dict[str, str]:
        """
        Extract video URL from <video> tag src attribute
        
        Args:
            soup: BeautifulSoup object of the HTML page
            
        Returns:
            Dictionary with quality as key and video URL as value
        """
        video_urls = {}
        video_tag = soup.find('video', class_='vjs-tech')
        
        if video_tag:
            src = video_tag.get('src', '')
            if src and '.mp4' in src and 'pixel.png' not in src:
                quality_match = re.search(REGEX_QUALITY_FROM_URL, src)
                if quality_match:
                    quality = quality_match.group(1)
                    src = src.replace('&amp;', '&')
                    video_urls[quality] = src
                    logger.debug(f"Extracted {quality}p from <video> tag: {src[:80]}...")
        
        return video_urls
    
    @staticmethod
    def extract_from_data_attributes(soup: BeautifulSoup) -> dict[str, str]:
        """
        Extract video URLs from data-player-* attributes
        
        Args:
            soup: BeautifulSoup object of the HTML page
            
        Returns:
            Dictionary with quality as key and video URL as value
        """
        video_urls = {}
        player_elements = soup.find_all(attrs={'data-player-1080': True})
        
        for element in player_elements:
            for quality in VIDEO_QUALITIES:
                attr_name = f'data-player-{quality}'
                url = element.get(attr_name, '')
                if url and '.mp4' in url:
                    url = url.replace('&amp;', '&')
                    video_urls[quality] = url
                    logger.debug(f"Extracted {quality}p from data-player-{quality}: {url[:80]}...")
        
        return video_urls
    
    @classmethod
    def extract_video_urls(cls, html: str) -> dict[str, str]:
        """
        Extract all video URLs from HTML
        
        Args:
            html: HTML content of the episode page
            
        Returns:
            Dictionary with quality as key and video URL as value
            
        Raises:
            VideoExtractionError: If no video URLs could be extracted
        """
        soup = BeautifulSoup(html, 'lxml')
        video_urls = {}
        
        methods = [
            cls.extract_from_source_tags,
            cls.extract_from_video_tag,
            cls.extract_from_data_attributes,
        ]
        
        for method in methods:
            try:
                urls = method(soup)
                video_urls.update(urls)
            except Exception as e:
                logger.warning(f"Error in {method.__name__}: {e}")
        
        if not video_urls:
            error_msg = "Could not extract video URLs from episode page"
            logger.error(error_msg)
            raise VideoExtractionError(error_msg)
        
        logger.info(f"Successfully extracted {len(video_urls)} video quality options: {', '.join(sorted(video_urls.keys(), key=int, reverse=True))}p")
        return video_urls
