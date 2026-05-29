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

def test_embed_logged_in():
    load_env()
    session_id = os.environ.get("INSTAGRAM_SESSION_ID", "").strip()
    user_id = os.environ.get("INSTAGRAM_USER_ID", "").strip()
    csrf_token = os.environ.get("INSTAGRAM_CSRF_TOKEN", "").strip()
    
    if not session_id or not user_id or not csrf_token:
        print("[ERROR] Credentials not found!")
        return
        
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = "https://www.instagram.com/p/CmYOR5Xq_OC/embed/"
    cookie_str = f"sessionid={session_id}; ds_user_id={user_id}; csrftoken={csrf_token}"
    
    cmd = [
        "curl.exe", "-s",
        "-A", ua,
        "-H", f"Cookie: {cookie_str}",
        "-H", f"X-CSRFToken: {csrf_token}",
        "-H", "Referer: https://www.instagram.com/",
        url
    ]
    
    print("Fetching Messi's post embed page WITH cookies...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = result.stdout
    
    print(f"Total Embed HTML size: {len(html)} bytes")
    
    with open("scratch/messi_embed_logged_in.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved to scratch/messi_embed_logged_in.html")
    
    # Check for keywords in HTML
    keywords = ["campeones", "messi", "leomessi", "argentina", "copa"]
    print("\n--- Keyword Occurrences in Logged In Embed ---")
    for kw in keywords:
        matches = [m.start() for m in re.finditer(re.escape(kw), html, re.IGNORECASE)]
        print(f"Keyword '{kw}': found {len(matches)} occurrences.")
        for idx, pos in enumerate(matches[:3]):
            snippet = html[max(0, pos-40):min(len(html), pos+120)]
            print(f"  Ocr {idx+1}: {repr(snippet)}")

    # Extract all application/json tags
    json_tags = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"\nFound {len(json_tags)} application/json script tags.")
    
    for idx, tag in enumerate(json_tags):
        content_lower = tag.lower()
        matched_kws = [k for k in keywords if k in content_lower]
        if len(matched_kws) > 1: # We want tags matching multiple keywords to be sure
            print(f"- Tag {idx} (size {len(tag)}) matched multiple: {matched_kws}")
            try:
                data = json.loads(tag)
                # save it
                out_path = f"scratch/messi_embed_logged_in_tag_{idx}.json"
                with open(out_path, "w", encoding="utf-8") as out_f:
                    json.dump(data, out_f, ensure_ascii=False, indent=2)
                print(f"  Saved parsed JSON to {out_path}")
            except Exception as e:
                print(f"  Error parsing: {e}")

if __name__ == "__main__":
    test_embed_logged_in()
