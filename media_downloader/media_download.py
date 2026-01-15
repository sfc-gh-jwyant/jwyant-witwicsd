import requests
import os
import re
import unicodedata

# --- CONFIGURATION ---
INPUT_FILE = "cities.txt"
USER_AGENT = "CityImageBot/1.3 (mailto:john@email.com)"
API_URL = "https://en.wikipedia.org/w/api.php"

# Use a session for better performance and persistent headers
session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def download_city_image(city_name, save_path_prefix):
    """
    Download the main page image for a city from Wikipedia.
    """
    params = {
        "action": "query",
        "format": "json",
        "titles": city_name,
        "prop": "pageimages",
        "pithumbsize": 1600,
        "redirects": 1
    }
    
    try:
        response = session.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for pid in pages:
            if int(pid) < 0:
                continue
                
            if "thumbnail" in pages[pid]:
                img_url = pages[pid]["thumbnail"]["source"]
                
                img_response = session.get(img_url, stream=True)
                img_response.raise_for_status()
                
                if len(img_response.content) > 0:
                    ext = img_url.split('.')[-1].split('?')[0].lower()
                    ext = 'jpg' if 'jpg' in ext else 'png' if 'png' in ext else ext
                    
                    full_path = f"{save_path_prefix}.{ext}"
                    
                    with open(full_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"   [✓] {full_path} ({len(img_response.content)} bytes)")
                    return True
    except Exception as e:
        print(f"   [X] Failed: {e}")
    
    print(f"   [!] No image found for: {city_name}")
    return False


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Missing {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r") as f:
        cities = [line.strip() for line in f if line.strip()]

    os.makedirs("media", exist_ok=True)
    
    for city in cities:
        print(f"📍 {city}")
        # Normalize unicode to remove accents (é→e, ü→u, etc.)
        normalized = unicodedata.normalize('NFKD', city.lower())
        # Keep only ASCII letters (a-z), remove everything else
        safe_city = re.sub(r'[^a-z]', '', normalized.encode('ascii', 'ignore').decode('ascii'))
        download_city_image(city, f"media/loc_{safe_city}")


if __name__ == "__main__":
    main()
