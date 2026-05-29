import subprocess
import re
import urllib.parse

def test():
    query = "make money with AI course"
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}&sp=EgIYAw%253D%253D"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    print(f"Fetching: {url}")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = res.stdout
    print(f"HTML Size: {len(html)} bytes")
    
    video_chunks = re.findall(r'"videoRenderer":(\{.*?\})\}', html)
    print(f"Found chunks: {len(video_chunks)}")
    
    for idx, chunk in enumerate(video_chunks[:10]):
        title_match = re.search(r'"title":\{"runs":\[\{"text":"([^"]+)"\}', chunk)
        title = title_match.group(1) if title_match else "Unknown"
        
        # Let's search for lengthText, simpleText, or accessibility
        simple_match = re.search(r'"lengthText":\{"simpleText":"([^"]+)"\}', chunk)
        access_match = re.search(r'"lengthText":\{"accessibility":\{"accessibilityData":\{"label":"([^"]+)"\}', chunk)
        
        simple_val = simple_match.group(1) if simple_match else "None"
        access_val = access_match.group(1) if access_match else "None"
        
        print(f"\n[{idx+1}] Title: {title}")
        print(f"  simpleText: {simple_val}")
        print(f"  accessibility label: {access_val}")

if __name__ == "__main__":
    test()
