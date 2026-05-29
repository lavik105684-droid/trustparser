import os
import subprocess
import re
import json

def analyze_instagram_html():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = "https://www.instagram.com/nasa/"
    
    cmd = [
        "curl.exe", "-s",
        "-A", ua,
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Referer: https://www.google.com/",
        url
    ]
    
    print("Fetching profile page...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = result.stdout
    
    print(f"HTML length: {len(html)}")
    if not html:
        print("Empty HTML returned.")
        return
        
    # Check for _sharedData
    shared_data_match = re.search(r'window\._sharedData\s*=\s*({.*?});', html)
    if shared_data_match:
        print("Found window._sharedData!")
        try:
            data = json.loads(shared_data_match.group(1))
            print("Successfully parsed window._sharedData JSON!")
            with open("scratch/shared_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("Saved to scratch/shared_data.json")
            return
        except Exception as e:
            print(f"Failed to parse _sharedData JSON: {e}")
            
    # Check for application/json script tags
    print("Searching for application/json script tags...")
    json_tags = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(json_tags)} application/json script tags.")
    
    parsed_count = 0
    for idx, tag_content in enumerate(json_tags):
        try:
            data = json.loads(tag_content)
            parsed_count += 1
            # Check if this data has user/profile info
            # Let's save each to see what they contain
            filename = f"scratch/json_tag_{idx}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
            
    print(f"Successfully parsed {parsed_count} json tags.")
    
    # Check if there is any other json variable
    additional_data = re.findall(r'window\.__additionalDataLoaded\s*\(\s*[\'"][^\'"]+[\'"]\s*,\s*({.*?})\s*\)\s*;', html)
    print(f"Found {len(additional_data)} __additionalDataLoaded matches.")
    for idx, data_str in enumerate(additional_data):
        try:
            data = json.loads(data_str)
            filename = f"scratch/additional_data_{idx}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved __additionalDataLoaded to {filename}")
        except Exception as e:
            print(f"Failed to parse additional data: {e}")

if __name__ == "__main__":
    analyze_instagram_html()
