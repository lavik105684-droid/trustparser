import os
import sys
import time
import json
import urllib.parse
import re
import subprocess

# Reconfigure standard output and standard error to UTF-8 for Windows encoding compatibility
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

CACHE_DIR = os.path.join("scratch", "botany_cache")
REGISTRY_FILE = os.path.join("scratch", "botany_registry.json")
CALIBRATION_FILE = os.path.join("scratch", "botany_calibration.json")

def clean_html(text):
    """Clean HTML entities and spaces."""
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#39;', "'", text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def search_youtube_raw(query, limit=30, long_only=False, min_minutes=20):
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
    curl_cmd = "curl" if os.name == "posix" else "curl.exe"
    cmd = [curl_cmd, "-s", "-L", "-A", ua, url]
    
    results = []
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = res.stdout
        blocks = html.split('"videoRenderer":{')
        
        for block in blocks[1:]:
            vid_match = re.search(r'"videoId":"([^"]{11})"', block)
            title_match = re.search(r'"title":\{"runs":\[\{"text":"([^"]+)"\}', block)
            length_match = re.search(r'"lengthText":\{"accessibility":\{"accessibilityData":\{"label":"[^"]+"\}\},"simpleText":"([^"]+)"\}', block)
            
            if vid_match:
                vid = vid_match.group(1)
                title = title_match.group(1) if title_match else "YouTube Video"
                title = clean_html(title)
                
                is_short = "short" in title.lower()
                
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
                            continue
                    else:
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
                        continue
                
                results.append({
                    "id": vid,
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "is_short": is_short
                })
                if len(results) >= limit:
                    break
                    
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

def bulk_crawl_youtube(queries_videos, queries_shorts, max_videos=0, max_shorts=0):
    start_time = time.time()
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # 1. Resolve max_videos and max_shorts using calibration file
    calibrated_videos = 10
    calibrated_shorts = 30
    
    if os.path.exists(CALIBRATION_FILE):
        try:
            with open(CALIBRATION_FILE, "r", encoding="utf-8") as c_f:
                cal = json.load(c_f)
                calibrated_videos = cal.get("max_videos", calibrated_videos)
                calibrated_shorts = cal.get("max_shorts", calibrated_shorts)
        except Exception:
            pass
            
    # Use calibrated limits if passed as 0
    if max_videos == 0:
        max_videos = calibrated_videos
        print(f"[CALIBRATION] Использование авто-калиброванных лимитов видео: {max_videos}")
    if max_shorts == 0:
        max_shorts = calibrated_shorts
        print(f"[CALIBRATION] Использование авто-калиброванных лимитов Shorts: {max_shorts}")
        
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
    
    # 1. Search long videos with self-healing fallback threshold
    thresholds = [20, 15, 10]
    for min_mins in thresholds:
        print(f"\n[CRAWLER] Попытка поиска длинных видео с порогом >= {min_mins} минут...")
        for idx, q in enumerate(queries_videos):
            if idx > 0:
                time.sleep(3.0)  # Cooldown between searches
            results = search_youtube_raw(q, limit=20, long_only=True, min_minutes=min_mins)
            for r in results:
                if r["id"] not in [v["id"] for v in discovered_videos]:
                    discovered_videos.append(r)
            if len(discovered_videos) >= max_videos * 2:
                break
        if len(discovered_videos) >= max_videos:
            print(f"[CRAWLER] Найдено достаточно длинных видео ({len(discovered_videos)}) с порогом >= {min_mins} мин.")
            break
        else:
            print(f"[CRAWLER-WARNING] Найдено только {len(discovered_videos)} видео с порогом >= {min_mins} мин. Пробуем следующий порог...")
            
    # 2. Search Shorts
    for idx, q in enumerate(queries_shorts):
        if idx > 0:
            time.sleep(3.0)
        results = search_youtube_raw(q, limit=20, long_only=False)
        for r in results:
            if r["is_short"] or "shorts" in q.lower():
                r["is_short"] = True
                if r["id"] not in [v["id"] for v in discovered_shorts]:
                    discovered_shorts.append(r)
        if len(discovered_shorts) >= max_shorts * 2:
            break
                    
    print(f"\n[CRAWLER-STATUS] Агрегировано кандидатов: {len(discovered_videos)} длинных видео, {len(discovered_shorts)} shorts.")
    
    # Limit to bounds
    target_videos = discovered_videos[:max_videos]
    target_shorts = discovered_shorts[:max_shorts]
    
    all_targets = target_videos + target_shorts
    total_targets = len(all_targets)
    
    print(f"[CRAWLER-STATUS] Начинаем сбор {total_targets} выбранных роликов...")
    
    scraped_count = 0
    for idx, t in enumerate(all_targets):
        vid_id = t["id"]
        
        # Save a registry entry
        if vid_id not in registry:
            registry[vid_id] = {
                "title": t["title"],
                "url": t["url"],
                "is_short": t["is_short"],
                "status": "pending_upload"
            }
            scraped_count += 1
            print(f"[{idx+1}/{total_targets}] [ДОБАВЛЕНО] {t['title']} ({vid_id}) [Short: {t['is_short']}]")
        else:
            print(f"[{idx+1}/{total_targets}] [УЖЕ В РЕЕСТРЕ] {t['title']} ({vid_id})")
            
    # Save registry
    with open(REGISTRY_FILE, "w", encoding="utf-8") as r_f:
        json.dump(registry, r_f, ensure_ascii=False, indent=2)
            
    # 2. Perform feedback loop calibration based on duration (Target: 30 seconds)
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n==================================================")
    print(f"[CALIBRATION] Сбор завершен за {duration:.2f} сек (Целевое время: 30 сек).")
    
    adjusted = False
    if duration < 28:
        calibrated_videos = min(200, int(calibrated_videos * 1.20) + 1)
        calibrated_shorts = min(1000, int(calibrated_shorts * 1.20) + 2)
        adjusted = True
        print(f"[CALIBRATION] Выполнение слишком быстрое. Лимиты увеличены: max_videos={calibrated_videos}, max_shorts={calibrated_shorts}")
    elif duration > 32:
        calibrated_videos = max(5, int(calibrated_videos * 0.85))
        calibrated_shorts = max(10, int(calibrated_shorts * 0.85))
        adjusted = True
        print(f"[CALIBRATION] Выполнение слишком медленное. Лимиты уменьшены: max_videos={calibrated_videos}, max_shorts={calibrated_shorts}")
    else:
        print(f"[CALIBRATION] Достигнута стабильная скорость выполнения (28-32 сек). Лимиты сохранены.")
        
    if adjusted or not os.path.exists(CALIBRATION_FILE):
        try:
            with open(CALIBRATION_FILE, "w", encoding="utf-8") as c_f:
                json.dump({
                    "max_videos": calibrated_videos, 
                    "max_shorts": calibrated_shorts, 
                    "last_duration": duration
                }, c_f, indent=2)
        except Exception as e:
            print(f"[CALIBRATION-ERROR] Не удалось сохранить файл калибровки: {e}")
            
    print(f"[CRAWLER-COMPLETE] Сбор ссылок успешно завершен!")
    print(f"Всего подготовлено для NotebookLM: {len(registry)} (Добавлено новых в этом запуске: {scraped_count})")
    print(f"==================================================")
    return registry

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-videos", type=int, default=0)
    parser.add_argument("--max-shorts", type=int, default=0)
    args = parser.parse_args()

    queries_videos = [
        "How to grow Alocasia at home guide",
        "Alocasia Jacklyn care indoor",
        "Alocasia Frydek variegata care",
        "Indoor plant grow light setup PPFD lux",
        "Foliage plant fertilizers NPK ratio",
        "Foliage soil mix DIY perlite vermiculite",
        "Hydroponics indoor setup home",
        "Growing lemon trees indoors guide",
        "How to grow figs indoors home",
        "Active grow lights indoor gardening",
        "NPK chemistry indoor plant care",
        "HB-101 plant growth stimulator review",
        "Superthrive fertilizer indoor plants guide",
        "Aktara insecticide indoor plants tripse",
        "How to treat spider mites house plants neem oil",
        "Soil moisture sensor smart home zigbee plant",
        "Alocasia watering hacks guide",
        "Variegated monster care indoor",
        "Growing indoor strawberries setup LED",
        "Root rot treatment indoor plants",
        "Indoor moss pole monstera setup",
        "Lechuza pon soil mix house plants",
        "Indoor citrus fertilizer chemistry",
        "Best soil mix for rare alocasias",
        "Houseplant smart watering systems DIY",
        "Cytokinin paste orchid alocasia propagation",
        "Grow lamps spectrum blue red white PPFD"
    ]
    queries_shorts = [
        "Alocasia propagation hack shorts",
        "Indoor grow lights comparison shorts",
        "NPK fertilizer houseplant shorts",
        "DIY soil mix house plants shorts",
        "Spider mite treatment neem oil shorts",
        "Root rot rescue alocasia shorts",
        "HB-101 plant hack shorts",
        "Smart plant sensor home assistant shorts",
        "Monstera repotting moss pole shorts",
        "Grow strawberries at home LED shorts"
    ]
    bulk_crawl_youtube(queries_videos, queries_shorts, max_videos=args.max_videos, max_shorts=args.max_shorts)
