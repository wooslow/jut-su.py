import logging
from jutsu_scraper import JutsuClient, setup_logger, VideoExtractionError, DownloadError, NetworkError


def main():
    """Example of batch downloading episodes"""
    setup_logger(level=logging.INFO)
    
    client = JutsuClient()
    
    username = "username"
    password = "if_you_read_this_pls_give_me_a_star_on_github_and_follow_me_on_github :)"
    anime_url = "https://jut.su/watari-ga-houkai/"
    
    try:
        client.login(username, password, anime_url)
        
        if not client.is_authenticated:
            print("✗ Login failed. Cannot download videos without authentication.")
            return
        
        print(f"✓ Login successful!\n")
        
        anime = client.get_anime_by_url(anime_url)
        if not anime:
            print("✗ Failed to parse anime")
            return
        
        print(f"Anime: {anime.title}")
        print(f"Total episodes: {len(anime.episodes)}")
        print(f"Seasons: {len(anime.seasons)}\n")
        
        if anime.seasons:
            print("Available seasons:")
            for season in anime.seasons:
                print(f"  Season {season.number}: {len(season.episodes)} episodes")
                if season.arcs:
                    print(f"    Arcs: {', '.join([arc.name for arc in season.arcs])}")
            print()
        
        print("Example 1: Download all episodes")
        print("-" * 50)
        downloaded = client.download_all_episodes(
            anime_url=anime_url,
            output_dir="watari_all_episodes",
            quality="720",
            show_progress=True
        )
        print(f"Downloaded {len(downloaded)} episodes\n")
        
        if anime.seasons:
            print("Example 2: Download season 1")
            print("-" * 50)
            downloaded = client.download_season(
                anime_url=anime_url,
                season_number=1,
                output_dir="watari_season_1",
                quality="720",
                show_progress=True
            )
            print(f"Downloaded {len(downloaded)} episodes\n")
            
            if anime.seasons[0].arcs:
                print("Example 3: Download first arc from season 1")
                print("-" * 50)
                arc_name = anime.seasons[0].arcs[0].name
                downloaded = client.download_arc(
                    anime_url=anime_url,
                    season_number=1,
                    arc_name=arc_name,
                    output_dir=f"watari_arc_{arc_name}",
                    quality="720",
                    show_progress=True
                )
                print(f"Downloaded {len(downloaded)} episodes\n")
        
        print("Example 4: Download specific episodes (1, 5, 10)")
        print("-" * 50)
        downloaded = client.download_episodes(
            anime_url=anime_url,
            episode_numbers=[1, 5, 10],
            output_dir="watari_selected",
            quality="720",
            show_progress=True
        )
        print(f"Downloaded {len(downloaded)} episodes\n")
        
    except (VideoExtractionError, DownloadError, NetworkError) as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()

