import json
from jutsu_scraper import JutsuClient


def main():
    """Example of exporting anime data to JSON"""
    client = JutsuClient()
    
    anime: Anime | None = client.get_anime("high-score-girl")
    
    if not anime:
        print("Failed to get anime")
        return
    
    anime_dict = anime.to_dict()
    
    output_file = "anime_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(anime_dict, f, ensure_ascii=False, indent=2)
    
    print(f"Anime data saved to {output_file}")
    print(f"Title: {anime_dict['title']}")
    print(f"Seasons: {len(anime_dict.get('seasons', []) or [])}")
    print(f"Episodes: {len(anime_dict['episodes'])}")


if __name__ == "__main__":
    main()

