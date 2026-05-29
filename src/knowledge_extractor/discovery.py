import subprocess
import re
import urllib.parse
import json

def clean_html(text):
    """Utility to clean basic HTML entities."""
    if not text:
        return ""
    text = text.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
    return text.strip()

def search_youtube(query, limit=5):
    """
    Performs a zero-dependency search on YouTube.
    Returns a list of dicts: [{'title': title, 'url': url}]
    """
    print(f"[DISCOVERY] Поиск на YouTube по запросу: '{query}'")
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    results = []
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = res.stdout
        
        # YouTube JSON search response has structures like:
        # "videoRenderer":{"videoId":"ID","thumbnail":...,"title":{"runs":[{"text":"TITLE"}]}}
        # Let's extract videoRenderer chunks
        video_chunks = re.findall(r'"videoRenderer":(\{.*?\})\}', html)
        
        for chunk in video_chunks:
            vid_match = re.search(r'"videoId":"([^"]+)"', chunk)
            title_match = re.search(r'"title":\{"runs":\[\{"text":"([^"]+)"\}', chunk)
            
            if vid_match:
                vid = vid_match.group(1)
                title = title_match.group(1) if title_match else "YouTube Video"
                title = clean_html(title)
                
                vid_url = f"https://www.youtube.com/watch?v={vid}"
                
                # De-duplicate
                if not any(r['url'] == vid_url for r in results):
                    results.append({
                        "title": title,
                        "url": vid_url,
                        "id": vid
                    })
                    if len(results) >= limit:
                        break
                        
        # Fallback if specific chunks fail but videoIds exist
        if not results:
            video_ids = re.findall(r'"videoId":"([^"]+)"', html)
            unique_ids = []
            for vid in video_ids:
                if vid not in unique_ids and len(vid) == 11:
                    unique_ids.append(vid)
            for vid in unique_ids[:limit]:
                results.append({
                    "title": "YouTube Video (Автоматически найдено)",
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "id": vid
                })
                
    except Exception as e:
        print(f"[DISCOVERY-ERROR] Ошибка поиска YouTube: {e}")
        
    print(f"[DISCOVERY] Найдено {len(results)} видеороликов на YouTube.")
    return results

def search_web(query, limit=5):
    """
    Performs a zero-dependency web search on DuckDuckGo.
    Returns a list of dicts: [{'title': title, 'url': url}]
    """
    print(f"[DISCOVERY] Поиск в Web по запросу: '{query}'")
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={query_encoded}"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    results = []
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = res.stdout
        
        # DuckDuckGo HTML structure for results:
        # <a class="result__snippet" href="//duckduckgo.com/l/?uddg=REAL_URL&amp;...">
        # class="result__snippet" usually contains snippet but the link is also in:
        # class="result__results" -> <a class="result__url" href="...">
        # Or class="result__snippet" or title link: <a class="result__a" href="//duckduckgo.com/l/?uddg=URL...">TITLE</a>
        
        # Let's extract title/link pairs using result__a
        matches = re.finditer(r'<a class="result__a"[^>]*href="//duckduckgo\.com/l/\?uddg=([^&"\']+)[^>]*>(.*?)</a>', html, re.DOTALL)
        
        for m in matches:
            raw_url = m.group(1)
            title = clean_html(m.group(2))
            actual_url = urllib.parse.unquote(raw_url)
            
            # Filter out advertisements or self links
            if "duckduckgo.com" not in actual_url and actual_url.startswith("http"):
                # Clean up title (remove strong tags or other markers)
                title = re.sub(r'<[^>]+>', '', title).strip()
                
                if not any(r['url'] == actual_url for r in results):
                    results.append({
                        "title": title,
                        "url": actual_url
                    })
                    if len(results) >= limit:
                        break
                        
    except Exception as e:
        print(f"[DISCOVERY-ERROR] Ошибка поиска Web: {e}")
        
    print(f"[DISCOVERY] Найдено {len(results)} веб-ссылок.")
    return results

def search_instagram(query, limit=5):
    """
    Performs a zero-dependency Instagram search via Picuki.
    Returns a list of dicts: [{'title': title, 'url': url, 'type': 'profile|hashtag'}]
    """
    print(f"[DISCOVERY] Поиск в Instagram по запросу: '{query}'")
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.picuki.com/search?q={query_encoded}"
    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    results = []
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = res.stdout
        
        # Accounts: href="https://www.picuki.com/profile/username"
        # Tags: href="https://www.picuki.com/tag/hashtag"
        accounts = list(set(re.findall(r'href="https://www\.picuki\.com/profile/([^"]+)"', html)))
        tags = list(set(re.findall(r'href="https://www\.picuki\.com/tag/([^"]+)"', html)))
        
        # Add accounts to results
        for acc in accounts[:limit]:
            results.append({
                "title": f"Instagram аккаунт: @{acc}",
                "url": f"https://www.instagram.com/{acc}/",
                "type": "profile"
            })
            
        # Add tags to results
        for t in tags[:limit]:
            if len(results) >= limit:
                break
            results.append({
                "title": f"Instagram хэштег: #{t}",
                "url": f"https://www.instagram.com/explore/tags/{t}/",
                "type": "hashtag"
            })
            
    except Exception as e:
        print(f"[DISCOVERY-ERROR] Ошибка поиска Instagram: {e}")
        
    print(f"[DISCOVERY] Найдено {len(results)} ресурсов Instagram.")
    return results

def discover_resources(query):
    """
    Aggregate search results from YouTube, Web and Instagram.
    """
    import time
    
    yt_results = search_youtube(query, limit=3)
    
    print("[DISCOVERY] Ожидание 2.5 секунд перед поиском в Web для защиты от блокировок...")
    time.sleep(2.5)
    
    web_results = search_web(query, limit=3)
    
    print("[DISCOVERY] Ожидание 2.5 секунд перед поиском в Instagram...")
    time.sleep(2.5)
    
    ig_results = search_instagram(query, limit=2)
    
    return {
        "query": query,
        "youtube": yt_results,
        "web": web_results,
        "instagram": ig_results
    }

if __name__ == "__main__":
    import sys
    q = "fastapi websocket" if len(sys.argv) < 2 else sys.argv[1]
    res = discover_resources(q)
    print("\n--- Агрегированные результаты ---")
    print(json.dumps(res, ensure_ascii=False, indent=2))
