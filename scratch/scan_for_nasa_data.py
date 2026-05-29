import os
import json
import re

def scan_all_tags_for_nasa():
    if not os.path.exists("scratch/logged_in_profile.html"):
        print("HTML file not found!")
        return
        
    with open("scratch/logged_in_profile.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    print(f"Scanning HTML ({len(html)} chars)...")
    
    # Extract all application/json tags
    json_tags = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(json_tags)} application/json script tags.")
    
    # We will search for keywords related to NASA's profile or posts
    # Since we know NASA's account has a high post count and username is 'nasa'
    for idx, tag in enumerate(json_tags):
        tag_len = len(tag)
        content_lower = tag.lower()
        
        # Search for NASA specific keywords or general media keywords
        has_nasa = "nasa" in content_lower
        has_media = "display_url" in tag or "shortcode" in tag or "dimensions" in tag
        
        if has_nasa or has_media:
            print(f"\n[TAG {idx}] Size: {tag_len} chars. Has NASA: {has_nasa}, Has Media: {has_media}")
            try:
                data = json.loads(tag)
                # Let's save it
                out_path = f"scratch/logged_in_tag_{idx}.json"
                with open(out_path, "w", encoding="utf-8") as out_f:
                    json.dump(data, out_f, ensure_ascii=False, indent=2)
                print(f"  Saved parsed JSON to {out_path}")
            except Exception as e:
                print(f"  Error parsing JSON: {e}")

if __name__ == "__main__":
    scan_all_tags_for_nasa()
