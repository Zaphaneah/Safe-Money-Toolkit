#!/usr/bin/env python3
"""Download royalty-free images for the Bible class presentation."""

import requests
import os
import time

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

# Primary and fallback URLs for each slide image
IMAGES = {
    "slide2_cross_mindset": [
        "https://images.pexels.com/photos/53959/pexels-photo-53959.jpeg?auto=compress&cs=tinysrgb&w=1920",
        "https://images.pexels.com/photos/2917373/pexels-photo-2917373.jpeg?auto=compress&cs=tinysrgb&w=1920",
    ],
    "slide3_incarnation": [
        "https://images.pexels.com/photos/753561/pexels-photo-753561.jpeg?auto=compress&cs=tinysrgb&w=1920",
        "https://images.pexels.com/photos/14692977/pexels-photo-14692977.jpeg?auto=compress&cs=tinysrgb&w=1920",
    ],
    "slide4_emptying": [
        "https://images.pexels.com/photos/6636605/pexels-photo-6636605.jpeg?auto=compress&cs=tinysrgb&w=1920",
        "https://images.pexels.com/photos/163762/pexels-photo-163762.jpeg?auto=compress&cs=tinysrgb&w=1920",
    ],
    "slide5_humble": [
        "https://images.pexels.com/photos/11061094/pexels-photo-11061094.jpeg?auto=compress&cs=tinysrgb&w=1920",
        "https://images.pexels.com/photos/10157945/pexels-photo-10157945.jpeg?auto=compress&cs=tinysrgb&w=1920",
    ],
    "slide6_cross_death": [
        "https://images.pexels.com/photos/20512337/pexels-photo-20512337.jpeg?auto=compress&cs=tinysrgb&w=1920",
        "https://images.pexels.com/photos/4330070/pexels-photo-4330070.jpeg?auto=compress&cs=tinysrgb&w=1920",
    ],
    "slide7_descending": [
        "https://images.pexels.com/photos/15505900/pexels-photo-15505900.jpeg?auto=compress&cs=tinysrgb&w=1920",
        "https://images.pexels.com/photos/2805636/pexels-photo-2805636.jpeg?auto=compress&cs=tinysrgb&w=1920",
    ],
    "slide8_serving_hands": [
        "https://images.pexels.com/photos/6646918/pexels-photo-6646918.jpeg?auto=compress&cs=tinysrgb&w=1920",
        "https://images.pexels.com/photos/6340692/pexels-photo-6340692.jpeg?auto=compress&cs=tinysrgb&w=1920",
    ],
    "slide9_contemplating": [
        "https://images.pexels.com/photos/3772618/pexels-photo-3772618.jpeg?auto=compress&cs=tinysrgb&w=1920",
        "https://images.pexels.com/photos/941555/pexels-photo-941555.jpeg?auto=compress&cs=tinysrgb&w=1920",
    ],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def download_image(name, urls):
    """Try downloading from primary URL, then fallbacks."""
    filepath = os.path.join(IMAGE_DIR, f"{name}.jpg")
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        print(f"  [SKIP] {name} already exists ({os.path.getsize(filepath)} bytes)")
        return filepath

    for i, url in enumerate(urls):
        try:
            print(f"  Trying URL {i+1}/{len(urls)} for {name}...")
            resp = requests.get(url, headers=HEADERS, timeout=30, stream=True)
            if resp.status_code == 200:
                content_type = resp.headers.get("Content-Type", "")
                if "image" in content_type or "jpeg" in content_type or "png" in content_type:
                    with open(filepath, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                    size = os.path.getsize(filepath)
                    if size > 5000:
                        print(f"  [OK] {name}: {size:,} bytes")
                        return filepath
                    else:
                        print(f"  [WARN] {name}: file too small ({size} bytes), trying next...")
                        os.remove(filepath)
                else:
                    print(f"  [WARN] {name}: unexpected content type: {content_type}")
            else:
                print(f"  [WARN] {name}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"  [ERR] {name}: {e}")
        time.sleep(0.5)

    print(f"  [FAIL] Could not download {name}")
    return None


def main():
    print("Downloading images for presentation...")
    results = {}
    for name, urls in IMAGES.items():
        result = download_image(name, urls)
        results[name] = result
        time.sleep(0.3)

    print("\n--- Summary ---")
    success = sum(1 for v in results.values() if v)
    print(f"Downloaded: {success}/{len(results)}")
    for name, path in results.items():
        status = "OK" if path else "FAILED"
        print(f"  {name}: {status}")

    return results


if __name__ == "__main__":
    main()
