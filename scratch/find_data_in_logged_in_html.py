import os
import subprocess
import re
import json

def load_env(env_path=".env"):
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def fetch_and_save_html():
    load_env()
    session_id = os.environ.get("INSTAGRAM_SESSION_ID", "").strip()
    user_id = os.environ.get("INSTAGRAM_USER_ID", "").strip()
    csrf_token = os.environ.get("INSTAGRAM_CSRF_TOKEN", "").strip()
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = "https://www.instagram.com/nasa/"
    cookie_str = f"sessionid={session_id}; ds_user_id={user_id}; csrftoken={csrf_token}"
    
    cmd = [
        "curl.exe", "-s",
        "-A", ua,
        "-H", f"Cookie: {cookie_str}",
        "-H", f"X-CSRFToken: {csrf_token}",
        "-H", "Referer: https://www.instagram.com/",
        url
    ]
    
    print("Fetching profile page...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = result.stdout
    
    with open("scratch/logged_in_profile.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved {len(html)} bytes to scratch/logged_in_profile.html")

def scan_html_for_data():
    if not os.path.exists("scratch/logged_in_profile.html"):
        print("HTML file not found!")
        return
        
    with open("scratch/logged_in_profile.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    print(f"Scanning HTML ({len(html)} chars)...")
    
    # 1. Search for any application/json tags
    json_tags = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(json_tags)} application/json script tags.")
    
    # 2. Check if any tag contains profile keywords
    keywords = ["edge_owner_to_timeline_media", "biography", "shortcode", "full_name", "display_url"]
    
    for idx, tag in enumerate(json_tags):
        tag_len = len(tag)
        found_keys = [k for k in keywords if k in tag]
        if found_keys:
            print(f"\n[TAG {idx}] Size: {tag_len} chars. Contains: {found_keys}")
            # Try to parse and find nested keys
            try:
                data = json.loads(tag)
                # Save it
                out_path = f"scratch/logged_in_tag_{idx}.json"
                with open(out_path, "w", encoding="utf-8") as out_f:
                    json.dump(data, out_f, ensure_ascii=False, indent=2)
                print(f"Saved parsed JSON to {out_path}")
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                # Save raw tag
                with open(f"scratch/logged_in_tag_{idx}_raw.txt", "w", encoding="utf-8") as out_f:
                    out_f.write(tag)

if __name__ == "__main__":
    fetch_and_save_html()
    scan_html_for_data()
