# Jut.su Scraper | jut-su.py

Modern Python library for parsing anime data from jut.su website.

> [!IMPORTANT]
> Is currently under development, so some features may not work properly or may not work at all


[![PyPI](https://img.shields.io/pypi/v/jut-su.py.svg)](https://pypi.org/project/jut-su.py/)
[![Python Version](https://img.shields.io/pypi/pyversions/jut-su.py.svg)](https://pypi.org/project/jut-su.py/)
[![License](https://img.shields.io/pypi/l/jut-su.py.svg)](https://pypi.org/project/jut-su.py/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/jut-su.py)
![Discord](https://img.shields.io/discord/1437280570643189873)


#### If you enjoy this project, please consider supporting it by giving it a star ⭐

### Support Discord:
> **[jut-su.py Community](https://discord.gg/6KZGsEfzq4)**

## Installation

```bash
pip install jut-su.py
```

## Quick Start

```python
from jutsu_scraper import JutsuClient

client = JutsuClient()

anime = client.get_anime("mayoiga")

if anime:
    print(f"Title: {anime.title}")
    print(f"Year: {anime.year}")
    print(f"Genres: {', '.join(anime.genres)}")
    print(f"Episodes: {len(anime.episodes)}")
```

### Custom Headers and Logging

```python
import logging
from jutsu_scraper import JutsuClient, setup_logger

setup_logger(level=logging.INFO)

client = JutsuClient(
    timeout=30,
    headers={
        "Custom-Header": "value"
    },
    use_random_ua=True,
    log_level=logging.INFO
)
```

### Authentication

```python
from jutsu_scraper import JutsuClient

client = JutsuClient()

# login_url can be any page URL (e.g., episode page)
success = client.login(
    username="your_username",
    password="your_password",
    login_url="https://jut.su/watari-ga-houkai/episode-19.html"
)

if success:
    print(f"Login successful! Authenticated: {client.is_authenticated}")
else:
    print("Login failed")
```

### Downloading Episodes

> [!WARNING]
> To download the video, you need to have a [jut-su plus](https://jut.su/plus/) subscription. 

```python
import logging
from jutsu_scraper import JutsuClient, setup_logger, VideoExtractionError, DownloadError, NetworkError

setup_logger(level=logging.INFO)

client = JutsuClient()

# Login first (required for accessing video URLs)
try:
    client.login("your_username", "your_password", "https://jut.su/anime/episode-1.html")
    
    episode_url = "https://jut.su/watari-ga-houkai/episode-19.html"
    video_urls = client.get_video_urls(episode_url)
    
    if video_urls:
        print(f"Available qualities: {', '.join(video_urls.keys())}p")
        
        output_path = client.download_episode(
            episode_url=episode_url,
            quality="720",  # Options: "1080", "720", "480", "360"
            output_path="episode_19.mp4",  # Optional: auto-generated if not provided
            show_progress=True
        )
        
        if output_path:
            print(f"Downloaded to: {output_path}")
            
except (VideoExtractionError, DownloadError, NetworkError) as e:
    print(f"Error: {e}")
```

### Batch Downloading

Download multiple episodes at once:

```python
from jutsu_scraper import JutsuClient

client = JutsuClient()
client.login("your_username", "your_password", "https://jut.su/anime/")

anime_url = "https://jut.su/watari-ga-houkai/"

# Download all episodes
downloaded = client.download_all_episodes(
    anime_url=anime_url,
    output_dir="episodes",
    quality="720"
)

# Download specific season
downloaded = client.download_season(
    anime_url=anime_url,
    season_number=1,
    output_dir="season_1",
    quality="720"
)

# Download specific arc
downloaded = client.download_arc(
    anime_url=anime_url,
    season_number=1,
    arc_name="Arc Name",
    output_dir="arc_name",
    quality="720"
)

# Download specific episodes by numbers
downloaded = client.download_episodes(
    anime_url=anime_url,
    episode_numbers=[1, 5, 10, 15],
    output_dir="selected_episodes",
    quality="720"
)
```

## Examples

See the `examples/` directory for more detailed examples:

- `examples/basic_usage.py` - Basic usage
- `examples/authentication.py` - User authentication
- `examples/download_episode.py` - Downloading single episode
- `examples/batch_download.py` - Batch downloading episodes
- `examples/seasons_and_arcs.py` - Working with seasons and arcs
- `examples/json_export.py` - Exporting to JSON

## Roadmap

Planned features for future releases:

- 📖 **Manga Support** - Parse manga data from jut.su
- 📺 **Large Series Support** - Enhanced support for long-running series

## Implemented Features

- ✅ **Authentication** - User authentication with username and password
- ✅ **Video Downloading** - Download anime episodes with quality selection
- ✅ **Batch Downloading** - Download multiple episodes, seasons, or arcs at once


## Contact me
- [Telegram](https://t.me/wooslow) | [Telegram Channel](https://t.me/wooslow_dev)
- [Discord](https://discord.gg/6KZGsEfzq4)
- private@wooslow.dev