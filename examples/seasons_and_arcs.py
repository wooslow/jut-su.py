from jutsu_scraper import JutsuClient


def main():
    """Example of parsing anime with seasons and arcs"""
    client = JutsuClient()
    
    anime: Anime | None = client.get_anime("overlord")
    
    if not anime:
        print("Failed to get anime")
        return
    
    print(f"Title: {anime.title}")
    print(f"Seasons: {len(anime.seasons)}")
    print(f"Total Episodes: {len(anime.episodes)}")
    print()
    
    for season in anime.seasons:
        print(f"Season {season.number}: {season.title or 'Untitled'}")
        print(f"  Episodes: {len(season.episodes)}")
        
        if season.arcs:
            print(f"  Arcs: {len(season.arcs)}")
            for arc in season.arcs:
                print(f"    - {arc.name}: {len(arc.episodes)} episodes")
                if arc.title:
                    print(f"      {arc.title}")


if __name__ == "__main__":
    main()

