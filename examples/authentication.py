import logging
from jutsu_scraper import JutsuClient, setup_logger, NetworkError


def main():
    """Example of using JutsuClient with authentication"""
    setup_logger(level=logging.INFO)
    
    client = JutsuClient()
    
    username = "username"
    password = "password"
    
    login_url = "https://jut.su/watari-ga-houkai/episode-19.html"
    
    try:
        success = client.login(username, password, login_url)
        
        if success:
            print(f"✓ Login successful! Authenticated: {client.is_authenticated}")
            episode_url = "https://jut.su/watari-ga-houkai/episode-19.html"
            
            try:
                response = client.session.get(episode_url, timeout=client.timeout)
                response.encoding = "windows-1251"
                html = response.text
                
                if html:
                    if "r421.yandexwebcache.org" in html or "yandexwebcache.org" in html:
                        print("✓ Authenticated content accessible - video sources available")
                    elif "pixel.png" in html:
                        print("⚠ Still seeing pixel.png - may need subscription (Jutsu+)")
                    else:
                        print("? Could not determine content access status")
            except Exception as e:
                print(f"Error accessing episode page: {e}")
        else:
            print("✗ Login failed. Please check your credentials.")
            
    except NetworkError as e:
        print(f"✗ Network error during login: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()

