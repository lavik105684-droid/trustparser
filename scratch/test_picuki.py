import os
import subprocess
import re

def test_picuki_profile(username="nasa"):
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = f"https://www.picuki.com/profile/{username}"
    
    cmd = [
        "curl.exe", "-s", "-L",
        "-A", ua,
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Referer: https://www.google.com/",
        url
    ]
    
    print(f"Fetching Picuki profile for @{username}...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = result.stdout
    
    print(f"HTML size: {len(html)} bytes")
    
    if not html:
        print("Empty HTML.")
        return False
        
    with open("scratch/picuki_profile.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved to scratch/picuki_profile.html")
    
    # Check for keywords
    print("\n--- Profile Scanning ---")
    if "profile-name" in html or "profile-header" in html or "biography" in html.lower() or username in html.lower():
        print("[SUCCESS] Detected profile page elements on Picuki!")
        # Find biography snippet
        bio_matches = re.findall(r'<div class="profile-description">(.*?)</div>', html, re.DOTALL)
        if bio_matches:
            print(f"- Biography found: {bio_matches[0].strip()}")
        # Find post shortcodes
        posts = re.findall(r'href="https://www.picuki.com/media/([^"]+)"', html)
        print(f"- Shortcodes found: {len(posts)} posts. Examples: {posts[:5]}")
        return True
    else:
        print("[FAIL] Could not identify profile content on Picuki.")
        return False

def test_picuki_media(shortcode="CmYOR5Xq_OC"):
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = f"https://www.picuki.com/media/{shortcode}"
    
    cmd = [
        "curl.exe", "-s", "-L",
        "-A", ua,
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Referer: https://www.google.com/",
        url
    ]
    
    print(f"\nFetching Picuki media post for shortcode {shortcode}...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = result.stdout
    
    print(f"HTML size: {len(html)} bytes")
    
    if not html:
        print("Empty HTML.")
        return False
        
    with open("scratch/picuki_media.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved to scratch/picuki_media.html")
    
    # Check for keywords
    print("\n--- Media Scanning ---")
    if "messi" in html.lower() or "campeones" in html.lower() or "post-description" in html.lower():
        print("[SUCCESS] Detected media elements on Picuki!")
        # Find description
        desc_matches = re.findall(r'<div class="post-description">(.*?)</div>', html, re.DOTALL)
        if desc_matches:
            print(f"- Description found: {desc_matches[0].strip()[:200]}...")
        return True
    else:
        print("[FAIL] Could not identify media content on Picuki.")
        return False

if __name__ == "__main__":
    profile_ok = test_picuki_profile()
    media_ok = test_picuki_media()
