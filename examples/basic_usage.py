from jutsu_scraper import JutsuClient


def main():
    """Basic example of using JutsuClient"""
    client = JutsuClient()
    
    anime: Anime | None = client.get_anime("mayoiga")
    
    if anime:
        print(f"Title: {anime.title}")
        print(f"Original Title: {anime.original_title}")
        print(f"Year: {anime.year}")
        print(f"Genres: {', '.join(anime.genres)}")
        print(f"Episodes: {len(anime.episodes)}")
        print(f"Description: {anime.description[:100] if anime.description else 'N/A'}...")
    else:
        print("Failed to get anime")


if __name__ == "__main__":
    main()

