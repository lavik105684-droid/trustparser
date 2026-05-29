import subprocess
import re
import urllib.parse
import json

def test_youtube_search(query="fastapi websocket"):
    print(f"--- Testing YouTube Search for: '{query}' ---")
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = result.stdout
        
        # YouTube embeds videoIds in the page JSON: "videoId":"kCc8FmEb1nY"
        video_ids = re.findall(r'"videoId":"([^"]+)"', html)
        # De-duplicate while preserving order
        unique_ids = []
        for vid in video_ids:
            if vid not in unique_ids and len(vid) == 11:
                unique_ids.append(vid)
                
        print(f"Found {len(unique_ids)} video IDs on YouTube search page.")
        for idx, vid in enumerate(unique_ids[:5]):
            print(f"  [{idx+1}] https://www.youtube.com/watch?v={vid}")
        return unique_ids
    except Exception as e:
        print("YouTube search error:", e)
        return []

def test_duckduckgo_search(query="fastapi websocket architecture"):
    print(f"\n--- Testing DuckDuckGo Search for: '{query}' ---")
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={query_encoded}"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = result.stdout
        
        # Extract search result links: <a class="result__url" href="URL">
        # DuckDuckGo HTML puts links inside: <a class="result__snippet" href="...url=URL..."> or similar
        # Let's inspect the actual HTML structure or search for links
        # Actually, DDG HTML uses: class="result__results" -> <a class="result__url" href="...">
        links = re.findall(r'href="([^"]+)"[^>]*class="result__url"', html)
        if not links:
            # Alternate search: find any outgoing links from results
            # DDG encodes actual external links inside their proxy links in /l/?kh=-1&uddg=URL
            proxy_links = re.findall(r'href="//duckduckgo\.com/l/\?uddg=([^&]+)', html)
            links = [urllib.parse.unquote(link) for link in proxy_links]
            
        # Filter links to include only valid web pages (not DDG domains)
        valid_links = []
        for l in links:
            if "duckduckgo.com" not in l and l.startswith("http"):
                valid_links.append(l)
                
        print(f"Found {len(valid_links)} web links on DuckDuckGo search page.")
        for idx, link in enumerate(valid_links[:5]):
            print(f"  [{idx+1}] {link}")
        return valid_links
    except Exception as e:
        print("DuckDuckGo search error:", e)
        return []

def test_picuki_search(query="python"):
    print(f"\n--- Testing Picuki Search for: '{query}' ---")
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.picuki.com/search?q={query_encoded}"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = result.stdout
        
        # Picuki search results contain a list of tags (hashtags) and accounts
        # Let's extract hashtag links or profiles
        # Accounts: href="https://www.picuki.com/profile/username"
        # Tags: href="https://www.picuki.com/tag/hashtag"
        accounts = list(set(re.findall(r'href="https://www.picuki\.com/profile/([^"]+)"', html)))
        tags = list(set(re.findall(r'href="https://www.picuki\.com/tag/([^"]+)"', html)))
        
        print(f"Found {len(accounts)} accounts and {len(tags)} hashtags on Picuki search page.")
        print(f"  Accounts: {accounts[:5]}")
        print(f"  Hashtags: {tags[:5]}")
        return accounts, tags
    except Exception as e:
        print("Picuki search error:", e)
        return [], []

if __name__ == "__main__":
    test_youtube_search()
    test_duckduckgo_search()
    test_picuki_search()
