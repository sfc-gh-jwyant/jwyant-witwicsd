import requests
import os
import re

# --- CONFIGURATION ---
INPUT_FILE = "cities.txt"
# Wikipedia requires a descriptive User-Agent. Change 'MyBot' to your name.
USER_AGENT = "CityLandmarkBot/1.1 (mailto:john@email.com)"
API_URL = "https://en.wikipedia.org/w/api.php"

# Use a session for better performance and persistent headers
session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

def download_image(title, save_path_prefix):
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "pageimages",
        "pithumbsize": 1200,
        "redirects": 1  # Follow redirects (e.g., 'NYC' -> 'New York City')
    }
    
    try:
        # 1. Get the image URL from API
        response = session.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for pid in pages:
            if "thumbnail" in pages[pid]:
                img_url = pages[pid]["thumbnail"]["source"]
                
                # 2. Download the actual image content
                img_response = session.get(img_url, stream=True)
                img_response.raise_for_status()
                
                # Check if we actually got data
                if len(img_response.content) > 0:
                    ext = img_url.split('.')[-1].split('?')[0].lower()
                    # Clean extension (handles .jpg?rev=123 issues)
                    ext = 'jpg' if 'jpg' in ext else 'png' if 'png' in ext else ext
                    
                    full_path = f"{save_path_prefix}.{ext}"
                    
                    with open(full_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"   [✓] Success: {full_path} ({len(img_response.content)} bytes)")
                    return True
        
        print(f"   [!] No image found for: {title}")
    except Exception as e:
        print(f"   [X] Failed to download {title}: {e}")
    return False

def download_city_image(city_name, save_path_prefix):
    """
    Download the best city image, preferring skyline/panorama images.
    First checks for skyline/panorama images on the page, then falls back to main image.
    """
    # First, try to find a skyline or panorama image from the page's image list
    params = {
        "action": "query",
        "format": "json",
        "titles": city_name,
        "prop": "images",
        "imlimit": 50,
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
            
            images = pages[pid].get("images", [])
            
            # Look for skyline/panorama images
            skyline_keywords = ["skyline", "panorama", "cityscape", "aerial", "view"]
            for img in images:
                img_title = img.get("title", "").lower()
                if any(kw in img_title for kw in skyline_keywords):
                    # Found a skyline/panorama image - get its URL
                    if download_commons_image(img.get("title"), save_path_prefix):
                        return True
        
        # Fallback: use the main page image
        print(f"   [i] No skyline image found, using main page image...")
        params = {
            "action": "query",
            "format": "json",
            "titles": city_name,
            "prop": "pageimages",
            "pithumbsize": 1600,
            "redirects": 1
        }
        
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
                    print(f"   [✓] City image (main): {full_path} ({len(img_response.content)} bytes)")
                    return True
    except Exception as e:
        print(f"   [X] Failed to download city image: {e}")
    
    print(f"   [!] No city image found for: {city_name}")
    return False


def download_commons_image(file_title, save_path_prefix):
    """
    Download an image from Wikimedia Commons by its File: title.
    """
    params = {
        "action": "query",
        "format": "json",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 1600,  # Request a thumbnail at this width
    }
    
    try:
        response = session.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for pid in pages:
            if int(pid) < 0:
                continue
            
            imageinfo = pages[pid].get("imageinfo", [])
            if imageinfo:
                # Prefer thumburl (resized), fall back to original url
                img_url = imageinfo[0].get("thumburl") or imageinfo[0].get("url")
                
                if img_url:
                    img_response = session.get(img_url, stream=True)
                    img_response.raise_for_status()
                    
                    if len(img_response.content) > 0:
                        ext = img_url.split('.')[-1].split('?')[0].lower()
                        ext = 'jpg' if 'jpg' in ext else 'png' if 'png' in ext else ext
                        
                        full_path = f"{save_path_prefix}.{ext}"
                        
                        with open(full_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"   [✓] City image (skyline): {full_path} ({len(img_response.content)} bytes)")
                        return True
    except Exception as e:
        pass
    
    return False

def find_landmarks(city_name):
    # Get coordinates first
    params = {"action": "query", "prop": "coordinates", "titles": city_name, "format": "json"}
    res = session.get(API_URL, params=params).json()
    pages = res.get("query", {}).get("pages", {})
    
    lat, lon = None, None
    for pid in pages:
        if "coordinates" in pages[pid]:
            lat = pages[pid]["coordinates"][0]["lat"]
            lon = pages[pid]["coordinates"][0]["lon"]
            break
            
    if lat is None: return []

    # Find nearby landmarks
    geo_params = {
        "action": "query", "list": "geosearch", "format": "json",
        "gscoord": f"{lat}|{lon}", "gsradius": 10000, "gslimit": 5
    }
    geo_res = session.get(API_URL, params=geo_params).json()
    return [item["title"] for item in geo_res.get("query", {}).get("geosearch", []) if item["title"] != city_name]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Missing {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r") as f:
        cities = [line.strip() for line in f if line.strip()]

    for city in cities:
        print(f"\n{'='*50}")
        print(f"Target: {city}")
        print(f"{'='*50}")
        
        # Clean folder/file name
        safe_city = re.sub(r'\W+', '_', city.lower())
        os.makedirs("downloads", exist_ok=True)

        # Download City image (prefer skyline/panorama)
        print(f"\n  📍 City Image:")
        download_city_image(city, f"downloads/loc_{safe_city}")

        # Download Landmarks (prefixed with loc_[city]_ for organization)
        print(f"\n  🏛️ Landmarks:")
        landmarks = find_landmarks(city)
        for lmark in landmarks:
            safe_lmark = re.sub(r'\W+', '_', lmark.lower())
            # Prefix: loc_[city]_[landmark]
            download_image(lmark, f"downloads/loc_{safe_city}_{safe_lmark}")

if __name__ == "__main__":
    main()