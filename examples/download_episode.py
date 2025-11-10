import logging
from jutsu_scraper import JutsuClient, setup_logger, VideoExtractionError, DownloadError, NetworkError


def main():
    """Example of downloading an episode"""
    setup_logger(level=logging.INFO)
    
    client = JutsuClient()
    
    username = "username"
    password = "password"
    
    episode_url = "https://jut.su/watari-ga-houkai/episode-19.html"
    
    try:
        success = client.login(username, password, episode_url)
        
        if not success:
            print("✗ Login failed. Cannot download video without authentication.")
            return
        
        print(f"✓ Login successful! Authenticated: {client.is_authenticated}\n")
        
        video_urls = client.get_video_urls(episode_url)
        
        if not video_urls:
            print("✗ Could not extract video URLs")
            return
        
        print(f"✓ Found {len(video_urls)} quality options:")
        for quality, url in sorted(video_urls.items(), key=lambda x: int(x[0]), reverse=True):
            print(f"  - {quality}p: {url[:80]}...")
        
        print(f"\nDownloading episode in 720p quality...")
        output_path = client.download_episode(
            episode_url=episode_url,
            quality="720",
            show_progress=True
        )
        
        if output_path:
            print(f"\n✓ Successfully downloaded to: {output_path}")
        else:
            print("\n✗ Download failed")
            
    except (VideoExtractionError, DownloadError, NetworkError) as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()

