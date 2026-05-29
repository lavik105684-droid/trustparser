import subprocess
import re
import urllib.parse

def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
    return text.strip()

def test_query(query):
    print(f"\nTesting query: '{query}'")
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}&sp=EgIYAw%253D%253D"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = res.stdout
    
    blocks = html.split('"videoRenderer":{')
    found = 0
    for block in blocks[1:]:
        vid_match = re.search(r'"videoId":"([^"]{11})"', block)
        title_match = re.search(r'"title":\{"runs":\[\{"text":"([^"]+)"\}', block)
        length_match = re.search(r'"lengthText":\{"accessibility":\{"accessibilityData":\{"label":"[^"]+"\}\},"simpleText":"([^"]+)"\}', block)
        
        if vid_match and length_match:
            vid = vid_match.group(1)
            title = clean_html(title_match.group(1)) if title_match else "Unknown"
            duration_str = length_match.group(1)
            parts = duration_str.split(":")
            
            is_long = False
            if len(parts) == 3:
                is_long = True
            elif len(parts) == 2:
                try:
                    if int(parts[0]) >= 40:
                        is_long = True
                except ValueError:
                    pass
                    
            if is_long:
                found += 1
                print(f"  [FOUND] {title} ({vid}) - Duration: {duration_str}")
    print(f"Total 40+ min videos found: {found}")
    return found

if __name__ == "__main__":
    test_query("Liam Ottley AI agency course")
    test_query("n8n full course tutorial 1 hour")
    test_query("make money with AI podcast 1 hour")
