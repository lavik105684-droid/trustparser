import subprocess
import re
import urllib.parse

def test():
    query = "make money with AI course"
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}&sp=EgIYAw%253D%253D"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = res.stdout
    
    video_chunks = re.findall(r'"videoRenderer":(\{.*?\})\}', html)
    if video_chunks:
        with open("scratch/chunk.json", "w", encoding="utf-8") as f:
            f.write(video_chunks[0])
        print("Successfully saved first chunk to scratch/chunk.json")

if __name__ == "__main__":
    test()
