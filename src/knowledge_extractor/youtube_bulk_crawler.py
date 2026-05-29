import os
import sys
import time
import json
import urllib.parse
import re
import subprocess

# Add current directory to path to import youtube_extractor and discovery
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from youtube_extractor import get_youtube_transcript, extract_video_id
from discovery import clean_html

CACHE_DIR = os.path.join("scratch", "yt_cache")
REGISTRY_FILE = os.path.join("scratch", "yt_registry.json")

def search_youtube_raw(query, limit=30, long_only=False, min_minutes=40):
    """
    Zero-dependency search on YouTube returning video details.
    Uses split-based HTML parsing and universal simpleText duration check.
    Supports dynamic minimum minutes filtering for long videos.
    """
    print(f"[CRAWLER] Поиск на YouTube по запросу: '{query}' [Фильтр >= {min_minutes} мин: {long_only}]")
    query_encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}"
    if long_only and min_minutes >= 20:
        url += "&sp=EgIYAw%253D%253D"  # Filter for Long (>20 mins)
        
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    
    results = []
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = res.stdout
        
        # Split HTML by videoRenderer block start to avoid lazy-matching JSON truncation
        blocks = html.split('"videoRenderer":{')
        
        for block in blocks[1:]:  # Skip the first block before any renderer
            vid_match = re.search(r'"videoId":"([^"]{11})"', block)
            title_match = re.search(r'"title":\{"runs":\[\{"text":"([^"]+)"\}', block)
            length_match = re.search(r'"lengthText":\{"accessibility":\{"accessibilityData":\{"label":"[^"]+"\}\},"simpleText":"([^"]+)"\}', block)
            
            if vid_match:
                vid = vid_match.group(1)
                title = title_match.group(1) if title_match else "YouTube Video"
                title = clean_html(title)
                
                # Default is_short detection
                is_short = "short" in title.lower()
                
                # Check duration in a language-independent way using simpleText (format: MM:SS or H:MM:SS)
                if length_match:
                    duration_str = length_match.group(1)
                    parts = duration_str.split(":")
                    
                    if long_only:
                        is_long_enough = False
                        if len(parts) == 3:  # H:MM:SS format
                            is_long_enough = True
                        elif len(parts) == 2:  # MM:SS format
                            try:
                                minutes = int(parts[0])
                                if minutes >= min_minutes:
                                    is_long_enough = True
                            except ValueError:
                                pass
                        if not is_long_enough:
                            continue  # Skip this video as it is under our minimum minutes threshold!
                    else:
                        # Short detection: duration under 1:30 or explicitly Short
                        if len(parts) == 2:
                            try:
                                minutes = int(parts[0])
                                seconds = int(parts[1])
                                if minutes == 0 or (minutes == 1 and seconds <= 30):
                                    is_short = True
                            except ValueError:
                                pass
                else:
                    if long_only:
                        continue  # Skip if length is unknown and we strictly want long videos
                
                results.append({
                    "id": vid,
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "is_short": is_short
                })
                if len(results) >= limit:
                    break
                    
        # Fallback using regex if no split blocks matched (cannot verify duration)
        if not results and not long_only:
            video_ids = re.findall(r'"videoId":"([^"]+)"', html)
            unique_ids = []
            for vid in video_ids:
                if vid not in unique_ids and len(vid) == 11:
                    unique_ids.append(vid)
            for vid in unique_ids[:limit]:
                results.append({
                    "id": vid,
                    "title": "YouTube Video (Автопоиск)",
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "is_short": False
                })
                
    except Exception as e:
        print(f"[CRAWLER-ERROR] Ошибка при поиске YouTube: {e}")
        
    print(f"[CRAWLER] Найдено {len(results)} видеороликов по запросу '{query}'")
    return results

def bulk_crawl_youtube(queries_videos, queries_shorts, max_videos=5, max_shorts=5):
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Load existing registry if available
    registry = {}
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as r_f:
                registry = json.load(r_f)
        except Exception:
            pass
            
    print(f"\n[CRAWLER] Запуск сбора: {max_videos} длинных видео (40+ мин) и {max_shorts} shorts...")
    
    discovered_videos = []
    discovered_shorts = []
    
    # 1. Search long videos with self-healing fallback threshold (40m -> 20m -> 12m)
    thresholds = [40, 20, 12]
    for min_mins in thresholds:
        print(f"\n[CRAWLER] Попытка поиска длинных видео с порогом >= {min_mins} минут...")
        for idx, q in enumerate(queries_videos):
            if idx > 0:
                time.sleep(3.0)  # Cooldown between searches
            results = search_youtube_raw(q, limit=20, long_only=True, min_minutes=min_mins)
            for r in results:
                if r["id"] not in [v["id"] for v in discovered_videos]:
                    discovered_videos.append(r)
            if len(discovered_videos) >= max_videos * 2:  # Get a buffer of candidates
                break
        if len(discovered_videos) >= max_videos:
            print(f"[CRAWLER] Найдено достаточно длинных видео ({len(discovered_videos)}) с порогом >= {min_mins} мин.")
            break
        else:
            print(f"[CRAWLER-WARNING] Найдено только {len(discovered_videos)} видео с порогом >= {min_mins} мин. Пробуем следующий порог...")
            
    # 2. Search Shorts
    for idx, q in enumerate(queries_shorts):
        if idx > 0:
            time.sleep(3.0)  # Cooldown between searches
        results = search_youtube_raw(q, limit=20, long_only=False)
        for r in results:
            if r["is_short"] or "shorts" in q.lower():
                r["is_short"] = True
                if r["id"] not in [v["id"] for v in discovered_shorts]:
                    discovered_shorts.append(r)
        if len(discovered_shorts) >= max_shorts * 2:
            break
                    
    print(f"\n[CRAWLER-STATUS] Агрегировано кандидатов: {len(discovered_videos)} длинных видео, {len(discovered_shorts)} shorts.")
    
    # Limit to requested bounds
    target_videos = discovered_videos[:max_videos]
    target_shorts = discovered_shorts[:max_shorts]
    
    all_targets = target_videos + target_shorts
    total_targets = len(all_targets)
    
    print(f"[CRAWLER-STATUS] Начинаем сбор {total_targets} выбранных роликов...")
    
    # Clear registry for a fresh run
    registry = {}
    scraped_count = 0
    
    # NOTE: Since local scraping of transcripts gets blocked by YouTube IP blocks,
    # we now only collect their metadata and save URLs to registry.
    # NotebookLM will pull the transcripts directly from Google cloud during import!
    for idx, t in enumerate(all_targets):
        vid_id = t["id"]
        
        # Save a registry entry so orchestrator can upload it directly via nlm
        registry[vid_id] = {
            "title": t["title"],
            "url": t["url"],
            "is_short": t["is_short"],
            "status": "pending_upload"
        }
        scraped_count += 1
        print(f"[{idx+1}/{total_targets}] [ДОБАВЛЕНО] {t['title']} ({vid_id}) [Short: {t['is_short']}]")
            
    # Save registry
    with open(REGISTRY_FILE, "w", encoding="utf-8") as r_f:
        json.dump(registry, r_f, ensure_ascii=False, indent=2)
            
    print(f"\n==================================================")
    print(f"[CRAWLER-COMPLETE] Сбор ссылок успешно завершен!")
    print(f"Всего подготовлено для NotebookLM: {len(registry)}")
    print(f"==================================================")
    return registry

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-videos", type=int, default=5)
    parser.add_argument("--max-shorts", type=int, default=5)
    args = parser.parse_args()

    queries_videos = [
        "AI side hustle 2026",
        "How to make money with AI",
        "AI passive income tools",
        "Faceless YouTube channel AI",
        "AI automation agency (AAA)",
        "Print on demand AI tutorial",
        "AI SaaS side hustle",
        "Making $1000/week with AI",
        "Automated AI blog setup",
        "AI content engine workflow",
        "Autopilot content creation",
        "Blog to video AI automation",
        "AI video generation workflow",
        "AI voiceover tutorial ElevenLabs",
        "AI automation workflows",
        "n8n AI agent tutorial",
        "No-code AI pipelines",
        "AI agents for workflow automation",
        "Gumloop tutorial / Make.com AI automation",
        "Automated data extraction AI",
        "Custom GPTs for business",
        "Connecting AI to database (ClickHouse / SQLite)",
        "Top AI tools 2026",
        "Next-gen AI video generators",
        "OpusClip alternatives / Descript AI tutorial",
        "HeyGen / Synthesia avatar tutorial",
        "CapCut Pro AI features",
        "Best AI extensions for creators"
    ]
    queries_shorts = [
        "Bulk create Shorts AI",
        "Faceless channel automation",
        "Automated faceless TikTok / Reels",
        "make money with AI shorts",
        "AI monetization hacks shorts",
        "AI side hustle shorts"
    ]
    # Crawl based on command line arguments
    bulk_crawl_youtube(queries_videos, queries_shorts, max_videos=args.max_videos, max_shorts=args.max_shorts)
