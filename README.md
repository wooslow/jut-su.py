# Jut.su Scraper | jut-su.py

Modern Python library for parsing anime data from jut.su website.

> Is currently under development, so some features may not work properly or may not work at all

[![PyPI](https://img.shields.io/pypi/v/jut-su.py.svg)](https://pypi.org/project/jut-su.py/)
[![Python Version](https://img.shields.io/pypi/pyversions/jut-su.py.svg)](https://pypi.org/project/jut-su.py/)
[![License](https://img.shields.io/pypi/l/jut-su.py.svg)](https://pypi.org/project/jut-su.py/)

## Installation

```bash
pip install jut-su.py
```

Or from source:

```bash
git clone <repository-url>
cd jut.su-scrapper
pip install -r requirements.txt
```

## Quick Start

```python
from jutsu_scraper import JutsuClient

# Create client
client = JutsuClient()

# Get anime information
anime = client.get_anime("mayoiga")

if anime:
    print(f"Title: {anime.title}")
    print(f"Year: {anime.year}")
    print(f"Genres: {', '.join(anime.genres)}")
    print(f"Episodes: {len(anime.episodes)}")
```

### Custom Headers

```python
client = JutsuClient(
    timeout=30,
    headers={
        "Custom-Header": "value"
    },
    use_random_ua=True  # Use random User-Agent for each request (default: True)
)
```

## Examples

See the `examples/` directory for more detailed examples:

- `examples/basic_usage.py` - Basic usage
- `examples/seasons_and_arcs.py` - Working with seasons and arcs
- `examples/json_export.py` - Exporting to JSON

## Roadmap

Planned features for future releases:

- 🎬 **Video Downloading** - Download anime episodes
- 🔐 **Authentication** - User authentication and viewing achievements
- 📖 **Manga Support** - Parse manga data from jut.su
- 📺 **Large Series Support** - Enhanced support for long-running series

## Requirements

- Python 3.10+
- `requests>=2.31.0`
- `beautifulsoup4>=4.12.0`
- `lxml>=4.9.0`
- `pydantic>=2.0.0`
- `fake-useragent>=1.4.0`

## Contact me
- [Telegram](https://t.me/wooslow) | [Telegram Channel](https://t.me/wooslow_dev)
- private@wooslow.dev