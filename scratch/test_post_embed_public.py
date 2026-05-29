import os
import subprocess
import re
import json

def test_embed_public():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = "https://www.instagram.com/p/CmYOR5Xq_OC/embed/"
    
    cmd = [
        "curl.exe", "-s", "-L", # -L to follow any redirects
        "-A", ua,
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Referer: https://www.google.com/",
        url
    ]
    
    print("Fetching Messi's World Cup post embed page...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = result.stdout
    
    print(f"Total Embed HTML size: {len(html)} bytes")
    
    with open("scratch/messi_embed.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved to scratch/messi_embed.html")
    
    # Check for keywords in HTML
    keywords = ["campeones", "messi", "leomessi", "argentina", "copa"]
    print("\n--- Keyword Occurrences in Embed ---")
    for kw in keywords:
        matches = [m.start() for m in re.finditer(re.escape(kw), html, re.IGNORECASE)]
        print(f"Keyword '{kw}': found {len(matches)} occurrences.")
        for idx, pos in enumerate(matches[:3]):
            snippet = html[max(0, pos-40):min(len(html), pos+120)]
            print(f"  Ocr {idx+1}: {repr(snippet)}")
            
    # Search for embed media or captions
    print("\n--- Search for Blockquote Caption ---")
    # Public embeds usually have a <blockquote> containing the caption
    bq_match = re.search(r'<blockquote[^>]*>(.*?)</blockquote>', html, re.DOTALL)
    if bq_match:
        print("Found blockquote!")
        print(bq_match.group(1)[:500])
    else:
        print("No blockquote found.")
        
    # Search for application/json script tags
    print("\n--- JSON script tags in Embed ---")
    json_tags = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(json_tags)} application/json script tags.")
    
    for idx, tag in enumerate(json_tags):
        content_lower = tag.lower()
        matched_kws = [k for k in keywords if k in content_lower]
        if matched_kws:
            print(f"- Tag {idx} (size {len(tag)}) matched: {matched_kws}")
            try:
                data = json.loads(tag)
                # print some keys
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())}")
                with open(f"scratch/messi_embed_tag_{idx}.json", "w", encoding="utf-8") as out_f:
                    json.dump(data, out_f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    test_embed_public()
