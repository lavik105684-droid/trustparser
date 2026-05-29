import subprocess
import re
import urllib.parse

def test():
    query = "n8n automation local docker"
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    print(f"Fetching: {url}")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = res.stdout
    print(f"HTML Size: {len(html)} bytes")
    
    if not html:
        print("Empty HTML!")
        return
        
    video_ids_regex = re.findall(r'"videoId":"([^"]+)"', html)
    print(f"Found videoIds via regex: {len(video_ids_regex)}")
    print(f"Sample IDs: {video_ids_regex[:10]}")
    
    video_chunks = re.findall(r'"videoRenderer":(\{.*?\})\}', html)
    print(f"Found videoRenderer chunks: {len(video_chunks)}")

if __name__ == "__main__":
    test()
