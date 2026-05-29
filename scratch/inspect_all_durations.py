import subprocess
import re
import urllib.parse

def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
    return text.strip()

def inspect(query):
    print(f"\nInspecting query: '{query}'")
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}&sp=EgIYAw%253D%253D"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = res.stdout
    
    blocks = html.split('"videoRenderer":{')
    print(f"Total blocks: {len(blocks)}")
    
    for idx, block in enumerate(blocks[1:15]):
        vid_match = re.search(r'"videoId":"([^"]{11})"', block)
        title_match = re.search(r'"title":\{"runs":\[\{"text":"([^"]+)"\}', block)
        length_match = re.search(r'"lengthText":\{"accessibility":\{"accessibilityData":\{"label":"[^"]+"\}\},"simpleText":"([^"]+)"\}', block)
        
        vid = vid_match.group(1) if vid_match else "None"
        title = clean_html(title_match.group(1)) if title_match else "None"
        duration = length_match.group(1) if length_match else "None"
        
        print(f"[{idx+1}] {title} ({vid}) - Duration: {duration}")

if __name__ == "__main__":
    inspect("Liam Ottley AI agency course")
