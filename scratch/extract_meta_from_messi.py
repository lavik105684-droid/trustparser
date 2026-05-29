import os
import subprocess
import re
import json

def extract_meta():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = "https://www.instagram.com/p/CmYOR5Xq_OC/"
    
    cmd = [
        "curl.exe", "-s",
        "-A", ua,
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Referer: https://www.google.com/",
        url
    ]
    
    print("Fetching Messi's World Cup post...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = result.stdout
    
    print(f"Total HTML size: {len(html)} bytes")
    
    with open("scratch/messi_post.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved to scratch/messi_post.html")
    
    # 1. Search for any meta tags in HTML
    print("\n--- Meta Tags ---")
    # We will search for any meta tag content
    meta_tags = re.findall(r'<meta[^>]*>', html)
    print(f"Found {len(meta_tags)} meta tags.")
    for tag in meta_tags:
        if any(p in tag for p in ["og:", "description", "title", "image", "video"]):
            print(tag)
            
    # 2. Search for any application/json scripts
    print("\n--- JSON script tags containing 'messi' or 'campeones' ---")
    json_tags = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(json_tags)} application/json script tags.")
    
    for idx, tag in enumerate(json_tags):
        if "messi" in tag.lower() or "shortcode" in tag or "campeones" in tag.lower():
            print(f"- Tag {idx} (size {len(tag)}) matched!")
            try:
                data = json.loads(tag)
                # Let's recursively search for caption or text in this JSON
                results = []
                def scan(obj, path=""):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            current_path = f"{path}.{k}" if path else k
                            if k in ["text", "caption", "shortcode", "display_url", "biography"]:
                                results.append((current_path, k, str(v)[:200]))
                            scan(v, current_path)
                    elif isinstance(obj, list):
                        for idx2, item in enumerate(obj):
                            scan(item, f"{path}[{idx2}]")
                scan(data)
                print(f"  Found {len(results)} matches:")
                for p, k, v in results[:10]:
                    print(f"    Path: {p} -> {k}: {v}")
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    extract_meta()
