import os
import re
from typing import Callable
import requests

from .logger import get_logger
from .exceptions import DownloadError, NetworkError
from .constants import REGEX_EPISODE_FROM_URL
from .types import VideoQuality, ProgressCallbackType

logger = get_logger(__name__)


class VideoDownloader:
    """Handle video downloading with progress tracking"""
    
    def __init__(self, session: requests.Session, timeout: int = 10) -> None:
        """
        Initialize downloader
        
        Args:
            session: Requests session to use for downloads
            timeout: Request timeout in seconds
        """
        self.session = session
        self.timeout = timeout
    
    def generate_filename(
        self,
        episode_url: str,
        quality: VideoQuality,
        output_path: str | None = None
    ) -> str:
        """
        Generate output filename for video
        
        Args:
            episode_url: URL of the episode page
            quality: Video quality
            output_path: Custom output path (optional)
            
        Returns:
            Generated filename
        """
        if output_path:
            return output_path
        
        episode_match = re.search(REGEX_EPISODE_FROM_URL, episode_url)
        if episode_match:
            anime_slug = episode_match.group(1)
            episode_num = episode_match.group(2)
            return f"{anime_slug}_episode_{episode_num}_{quality}p.mp4"
        
        return f"episode_{quality}p.mp4"
    
    def ensure_output_directory(self, output_path: str) -> None:
        """
        Ensure output directory exists
        
        Args:
            output_path: Path to output file
        """
        output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else '.'
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.debug(f"Created output directory: {output_dir}")
    
    def download(
        self,
        video_url: str,
        output_path: str,
        chunk_size: int = 8192,
        progress_callback: ProgressCallbackType = None
    ) -> str:
        """
        Download video file
        
        Args:
            video_url: URL of the video file
            output_path: Path to save the video
            chunk_size: Chunk size for downloading
            progress_callback: Optional callback function(downloaded, total)
            
        Returns:
            Path to downloaded file
            
        Raises:
            DownloadError: If download fails
            NetworkError: If network request fails
        """
        try:
            logger.info(f"Starting download: {video_url[:80]}...")
            logger.debug(f"Output path: {output_path}")
            
            self.ensure_output_directory(output_path)
            
            response = self.session.get(video_url, stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)
            
            logger.info(f"Successfully downloaded video: {output_path} ({downloaded} bytes)")
            return output_path
            
        except requests.RequestException as e:
            error_msg = f"Network error during download: {e}"
            logger.error(error_msg)
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    logger.debug(f"Removed partial file: {output_path}")
                except OSError:
                    pass
            raise NetworkError(error_msg) from e
        except OSError as e:
            error_msg = f"File system error during download: {e}"
            logger.error(error_msg)
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass
            raise DownloadError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during download: {e}"
            logger.error(error_msg)
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass
            raise DownloadError(error_msg) from e


def format_progress(downloaded: int, total: int) -> str:
    """
    Format download progress for display
    
    Args:
        downloaded: Bytes downloaded
        total: Total bytes to download
        
    Returns:
        Formatted progress string
    """
    if total == 0:
        return f"Downloading: {downloaded} bytes"
    
    percent = (downloaded / total) * 100
    return f"Downloading: {percent:.1f}% ({downloaded}/{total} bytes)"
