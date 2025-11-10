"""
Main client for parsing data from jut.su website
"""
from typing import Callable
import os
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from .models.anime import Anime
from .models.episode import Episode
from .models.season import Season
from .models.arc import Arc
from .constants import BASE_URL, DEFAULT_ENCODING
from .logger import get_logger
from .exceptions import (
    AuthenticationError,
    VideoExtractionError,
    DownloadError,
    NetworkError,
    ParseError
)
from .video_extractor import VideoExtractor
from .downloader import VideoDownloader, format_progress
from .types import (
    VideoQuality,
    ProgressCallbackType,
    BatchProgressCallbackType,
)

logger = get_logger(__name__)
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
    
    def __init__(
        self,
        timeout: int = 10,
        headers: dict[str, str] | None = None,
        use_random_ua: bool = True,
        log_level: int | None = None
    ) -> None:
        """
        Initialize client
        
        Args:
            timeout: Request timeout in seconds
            headers: Additional HTTP headers (merged with defaults)
            use_random_ua: Whether to use random User-Agent for each request (default: True)
            log_level: Logging level (default: WARNING). Set to logging.INFO or logging.DEBUG for more verbose output
        """
        self.timeout = timeout
        self.use_random_ua = use_random_ua
        self.session = requests.Session()
        self.is_authenticated = False
        
        if log_level is not None:
            logger.setLevel(log_level)
        
        default_headers = _get_default_headers()
        if headers:
            default_headers.update(headers)
        
        self.session.headers.update(default_headers)
        
        self._video_extractor = VideoExtractor()
        self._downloader = VideoDownloader(self.session, timeout)
        
        logger.debug("JutsuClient initialized")
    
    def _get_html(self, url: str) -> str | None:
        """
        Get HTML content from URL
        
        Args:
            url: Page URL
            
        Returns:
            HTML content or None on error
        """
        try:
            if self.use_random_ua:
                try:
                    self.session.headers["User-Agent"] = _ua.random
                except Exception:
                    logger.warning("Failed to update User-Agent, keeping existing")
            
            logger.debug(f"Requesting URL: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = DEFAULT_ENCODING
            response.raise_for_status()
            logger.debug(f"Successfully retrieved HTML from {url}")
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error requesting {url}: {e}")
            return None
    
    def get_anime(self, anime_slug: str) -> Anime | None:
        """
        Get anime information by slug
        
        Args:
            anime_slug: Anime slug (e.g., 'mayoiga')
            
        Returns:
            Anime object or None on error
        """
        url = f"{self.BASE_URL}/{anime_slug}/"
        logger.info(f"Fetching anime: {anime_slug}")
        html = self._get_html(url)
        
        if not html:
            logger.warning(f"Failed to retrieve HTML for anime: {anime_slug}")
            return None
        
        try:
            anime = Anime.from_html(html, url)
            logger.info(f"Successfully parsed anime: {anime.title if anime else 'Unknown'}")
            return anime
        except Exception as e:
            logger.error(f"Error parsing anime {anime_slug}: {e}")
            return None
    
    def get_anime_by_url(self, url: str) -> Anime | None:
        """
        Get anime information by full URL
        
        Args:
            url: Full anime page URL
            
        Returns:
            Anime object or None on error
        """
        logger.info(f"Fetching anime from URL: {url}")
        html = self._get_html(url)
        
        if not html:
            logger.warning(f"Failed to retrieve HTML from URL: {url}")
            return None
        
        try:
            anime = Anime.from_html(html, url)
            logger.info(f"Successfully parsed anime: {anime.title if anime else 'Unknown'}")
            return anime
        except Exception as e:
            logger.error(f"Error parsing anime from URL {url}: {e}")
            return None
    
    def login(
        self,
        username: str,
        password: str,
        login_url: str | None = None
    ) -> bool:
        """
        Authenticate user with username and password
        
        Args:
            username: Login name or email
            password: User password
            login_url: URL to send login request to (default: BASE_URL)
                      Can be any page URL (e.g., episode page URL)
            
        Returns:
            True if login successful, False otherwise
            
        Raises:
            AuthenticationError: If login fails with a clear error
        """
        if not login_url:
            login_url = self.BASE_URL
        
        logger.info(f"Attempting login for user: {username}")
        
        try:
            self.session.get(login_url, timeout=self.timeout)
        except requests.RequestException as e:
            logger.warning(f"Failed to get login page, continuing anyway: {e}")
        
        login_data = {
            "login_name": username,
            "login_password": password,
            "login": "submit"
        }
        
        try:
            post_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": login_url,
                "Origin": self.BASE_URL,
            }
            
            response = self.session.post(
                login_url,
                data=login_data,
                headers=post_headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.encoding = DEFAULT_ENCODING
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            
            login_panel = soup.select_one("#topLoginPanel")
            if login_panel:
                self.is_authenticated = True
                logger.info("Login successful")
                return True
            
            login_form = soup.select_one("form.login_panel_f")
            if login_form:
                error_messages = soup.find_all(
                    string=lambda text: text and (
                        "неверный" in text.lower() or 
                        "ошибка" in text.lower() or
                        "error" in text.lower()
                    )
                )

                if error_messages:
                    self.is_authenticated = False
                    logger.warning("Login failed: Invalid credentials")
                    return False
                
                self.is_authenticated = False
                logger.warning("Login failed: Could not determine status")
                return False
            
            if "topLoginPanel" not in html and "login_panel_f" not in html:
                self.is_authenticated = True
                logger.info("Login successful (redirect detected)")
                return True
            
            self.is_authenticated = False
            logger.warning("Login failed: Could not determine authentication status")
            return False
            
        except requests.RequestException as e:
            error_msg = f"Network error during login: {e}"
            logger.error(error_msg)
            self.is_authenticated = False
            raise NetworkError(error_msg) from e
    
    def get_video_urls(self, episode_url: str) -> dict[str, str] | None:
        """
        Extract video URLs from episode page
        
        Args:
            episode_url: URL of the episode page
            
        Returns:
            Dictionary with quality as key and video URL as value
            Example: {"1080": "https://...", "720": "https://...", ...}
            Returns None on error
            
        Raises:
            VideoExtractionError: If video URLs could not be extracted
        """
        logger.info(f"Extracting video URLs from: {episode_url}")
        html = self._get_html(episode_url)
        
        if not html:
            logger.error(f"Failed to retrieve HTML from episode URL: {episode_url}")
            return None
        
        try:
            video_urls = self._video_extractor.extract_video_urls(html)
            return video_urls
        except VideoExtractionError as e:
            logger.error(f"Failed to extract video URLs: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during video URL extraction: {e}")
            return None
    
    def download_episode(
        self,
        episode_url: str,
        output_path: str | None = None,
        quality: VideoQuality = "720",
        chunk_size: int = 8192,
        show_progress: bool = True,
        progress_callback: ProgressCallbackType = None
    ) -> str | None:
        """
        Download episode video
        
        Args:
            episode_url: URL of the episode page
            output_path: Path to save the video file (default: auto-generated)
            quality: Video quality ("1080", "720", "480", "360") - default: "720"
            chunk_size: Chunk size for downloading (default: 8192)
            show_progress: Whether to show download progress using default callback (default: True)
            progress_callback: Optional custom callback function(downloaded, total) for progress updates
            
        Returns:
            Path to downloaded file or None on error
            
        Raises:
            VideoExtractionError: If video URLs could not be extracted
            DownloadError: If download fails
            NetworkError: If network request fails
        """
        logger.info(f"Starting episode download from: {episode_url}")
        
        video_urls = self.get_video_urls(episode_url)
        if not video_urls:
            error_msg = "Could not extract video URLs from episode page"
            logger.error(error_msg)
            raise VideoExtractionError(error_msg)
        
        if quality not in video_urls:
            available_qualities = list(video_urls.keys())
            logger.warning(
                f"Quality {quality}p not available. Available qualities: {', '.join(available_qualities)}p"
            )
            quality = max(available_qualities, key=int)
            logger.info(f"Using quality {quality}p instead")
        
        video_url = video_urls[quality]
        
        output_path = self._downloader.generate_filename(episode_url, quality, output_path)
        
        if show_progress and progress_callback is None:
            def default_progress_callback(downloaded: int, total: int) -> None:
                progress_str = format_progress(downloaded, total)
                print(f"\r{progress_str}", end='', flush=True)
            
            progress_callback = default_progress_callback
        
        try:
            result_path = self._downloader.download(
                video_url=video_url,
                output_path=output_path,
                chunk_size=chunk_size,
                progress_callback=progress_callback
            )
            
            if show_progress and progress_callback:
                print()
            
            logger.info(f"Successfully downloaded episode to: {result_path}")
            return result_path
            
        except (DownloadError, NetworkError) as e:
            logger.error(f"Download failed: {e}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error during download: {e}"
            logger.error(error_msg)
            raise DownloadError(error_msg) from e
    
    def download_all_episodes(
        self,
        anime_url: str,
        output_dir: str | None = None,
        quality: VideoQuality = "720",
        chunk_size: int = 8192,
        show_progress: bool = True,
        progress_callback: BatchProgressCallbackType = None
    ) -> list[str]:
        """
        Download all episodes from anime page
        
        Args:
            anime_url: URL of the anime page (e.g., "https://jut.su/watari-ga-houkai/")
            output_dir: Directory to save episodes (default: current directory)
            quality: Video quality ("1080", "720", "480", "360") - default: "720"
            chunk_size: Chunk size for downloading (default: 8192)
            show_progress: Whether to show download progress (default: True)
            progress_callback: Optional callback function(current, total, episode_num, total_episodes)
            
        Returns:
            List of paths to downloaded files
            
        Raises:
            VideoExtractionError: If video URLs could not be extracted
            DownloadError: If download fails
            NetworkError: If network request fails
        """
        anime = self.get_anime_by_url(anime_url)
        if not anime:
            raise ParseError(f"Failed to parse anime from URL: {anime_url}")
        
        episodes = anime.episodes
        if not episodes:
            logger.warning("No episodes found")
            return []
        
        logger.info(f"Starting download of {len(episodes)} episodes")
        return self._download_episodes_list(
            episodes=episodes,
            output_dir=output_dir,
            quality=quality,
            chunk_size=chunk_size,
            show_progress=show_progress,
            progress_callback=progress_callback
        )
    
    def download_season(
        self,
        anime_url: str,
        season_number: int,
        output_dir: str | None = None,
        quality: VideoQuality = "720",
        chunk_size: int = 8192,
        show_progress: bool = True,
        progress_callback: BatchProgressCallbackType = None
    ) -> list[str]:
        """
        Download all episodes from a specific season
        
        Args:
            anime_url: URL of the anime page (e.g., "https://jut.su/watari-ga-houkai/")
            season_number: Season number to download
            output_dir: Directory to save episodes (default: current directory)
            quality: Video quality ("1080", "720", "480", "360") - default: "720"
            chunk_size: Chunk size for downloading (default: 8192)
            show_progress: Whether to show download progress (default: True)
            progress_callback: Optional callback function(current, total, episode_num, total_episodes)
            
        Returns:
            List of paths to downloaded files
            
        Raises:
            VideoExtractionError: If video URLs could not be extracted
            DownloadError: If download fails
            NetworkError: If network request fails
        """
        anime = self.get_anime_by_url(anime_url)
        if not anime:
            raise ParseError(f"Failed to parse anime from URL: {anime_url}")
        
        season = next((s for s in anime.seasons if s.number == season_number), None)
        if not season:
            raise ValueError(f"Season {season_number} not found")
        
        episodes = season.episodes
        if not episodes:
            logger.warning(f"No episodes found in season {season_number}")
            return []
        
        logger.info(f"Starting download of season {season_number} ({len(episodes)} episodes)")
        return self._download_episodes_list(
            episodes=episodes,
            output_dir=output_dir,
            quality=quality,
            chunk_size=chunk_size,
            show_progress=show_progress,
            progress_callback=progress_callback
        )
    
    def download_arc(
        self,
        anime_url: str,
        season_number: int,
        arc_name: str,
        output_dir: str | None = None,
        quality: VideoQuality = "720",
        chunk_size: int = 8192,
        show_progress: bool = True,
        progress_callback: BatchProgressCallbackType = None
    ) -> list[str]:
        """
        Download all episodes from a specific arc
        
        Args:
            anime_url: URL of the anime page (e.g., "https://jut.su/watari-ga-houkai/")
            season_number: Season number containing the arc
            arc_name: Name of the arc to download
            output_dir: Directory to save episodes (default: current directory)
            quality: Video quality ("1080", "720", "480", "360") - default: "720"
            chunk_size: Chunk size for downloading (default: 8192)
            show_progress: Whether to show download progress (default: True)
            progress_callback: Optional callback function(current, total, episode_num, total_episodes)
            
        Returns:
            List of paths to downloaded files
            
        Raises:
            VideoExtractionError: If video URLs could not be extracted
            DownloadError: If download fails
            NetworkError: If network request fails
        """
        anime = self.get_anime_by_url(anime_url)
        if not anime:
            raise ParseError(f"Failed to parse anime from URL: {anime_url}")
        
        season = next((s for s in anime.seasons if s.number == season_number), None)
        if not season:
            raise ValueError(f"Season {season_number} not found")
        
        arc = next((a for a in season.arcs if a.name == arc_name), None)
        if not arc:
            raise ValueError(f"Arc '{arc_name}' not found in season {season_number}")
        
        episodes = arc.episodes
        if not episodes:
            logger.warning(f"No episodes found in arc '{arc_name}'")
            return []
        
        logger.info(f"Starting download of arc '{arc_name}' ({len(episodes)} episodes)")
        return self._download_episodes_list(
            episodes=episodes,
            output_dir=output_dir,
            quality=quality,
            chunk_size=chunk_size,
            show_progress=show_progress,
            progress_callback=progress_callback
        )
    
    def download_episodes(
        self,
        anime_url: str,
        episode_numbers: list[int],
        output_dir: str | None = None,
        quality: VideoQuality = "720",
        chunk_size: int = 8192,
        show_progress: bool = True,
        progress_callback: BatchProgressCallbackType = None
    ) -> list[str]:
        """
        Download specific episodes by their numbers
        
        Args:
            anime_url: URL of the anime page (e.g., "https://jut.su/watari-ga-houkai/")
            episode_numbers: List of episode numbers to download
            output_dir: Directory to save episodes (default: current directory)
            quality: Video quality ("1080", "720", "480", "360") - default: "720"
            chunk_size: Chunk size for downloading (default: 8192)
            show_progress: Whether to show download progress (default: True)
            progress_callback: Optional callback function(current, total, episode_num, total_episodes)
            
        Returns:
            List of paths to downloaded files
            
        Raises:
            VideoExtractionError: If video URLs could not be extracted
            DownloadError: If download fails
            NetworkError: If network request fails
        """
        anime = self.get_anime_by_url(anime_url)
        if not anime:
            raise ParseError(f"Failed to parse anime from URL: {anime_url}")
        
        episodes = [ep for ep in anime.episodes if ep.number in episode_numbers]
        if not episodes:
            logger.warning(f"No episodes found with numbers: {episode_numbers}")
            return []
        
        logger.info(f"Starting download of {len(episodes)} episodes: {episode_numbers}")
        return self._download_episodes_list(
            episodes=episodes,
            output_dir=output_dir,
            quality=quality,
            chunk_size=chunk_size,
            show_progress=show_progress,
            progress_callback=progress_callback
        )
    
    def _download_episodes_list(
        self,
        episodes: list[Episode],
        output_dir: str | None = None,
        quality: VideoQuality = "720",
        chunk_size: int = 8192,
        show_progress: bool = True,
        progress_callback: BatchProgressCallbackType = None
    ) -> list[str]:
        """
        Internal method to download a list of episodes
        
        Args:
            episodes: List of Episode objects to download
            output_dir: Directory to save episodes
            quality: Video quality
            chunk_size: Chunk size for downloading
            show_progress: Whether to show download progress
            progress_callback: Optional callback function(current, total, episode_num, total_episodes)
            
        Returns:
            List of paths to downloaded files
        """
        downloaded_files = []
        total_episodes = len(episodes)
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        for idx, episode in enumerate(episodes, 1):
            try:
                logger.info(f"Downloading episode {episode.number} ({idx}/{total_episodes})")
                
                if output_dir:
                    output_path = os.path.join(output_dir, f"episode_{episode.number}_{quality}p.mp4")
                else:
                    output_path = None
                
                if show_progress and progress_callback is None:
                    def episode_progress_callback(downloaded: int, total: int) -> None:
                        progress_str = format_progress(downloaded, total)
                        print(f"\r[{idx}/{total_episodes}] Episode {episode.number}: {progress_str}", end='', flush=True)
                    
                    episode_callback = episode_progress_callback
                elif progress_callback:
                    def episode_progress_callback(downloaded: int, total: int) -> None:
                        progress_callback(downloaded, total, episode.number, total_episodes)
                    
                    episode_callback = episode_progress_callback
                else:
                    episode_callback = None
                
                file_path = self.download_episode(
                    episode_url=episode.url,
                    output_path=output_path,
                    quality=quality,
                    chunk_size=chunk_size,
                    show_progress=show_progress,
                    progress_callback=episode_callback
                )
                
                if file_path:
                    downloaded_files.append(file_path)
                    logger.info(f"Successfully downloaded episode {episode.number}: {file_path}")
                else:
                    logger.error(f"Failed to download episode {episode.number}")
                    
            except Exception as e:
                logger.error(f"Error downloading episode {episode.number}: {e}")
                continue
            
            if show_progress and not progress_callback:
                print()
        
        logger.info(f"Downloaded {len(downloaded_files)}/{total_episodes} episodes")
        return downloaded_files
