import subprocess
import re
import sys

def clean_html(text):
    """Utility to remove HTML tags and normalize whitespace."""
    if not text:
        return ""
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode basic HTML entities
    text = text.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
    return text.strip()

def scrape_picuki_profile(username):
    """Scrapes profile metadata and recent posts from Picuki."""
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = f"https://www.picuki.com/profile/{username}"
    
    cmd = [
        "curl.exe", "-s", "-L",
        "-A", ua,
        "-H", "Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "-H", "Referer: https://www.google.com/",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = result.stdout
        
        if not html or "profile-name" not in html:
            return None
            
        # Parse profile details
        username_match = re.search(r'<div class="profile-name">[^@]*@([^<]+)</div>', html)
        extracted_username = username_match.group(1).strip() if username_match else username
        
        fullname_match = re.search(r'<h1 class="profile-title">([^<]+)</h1>', html)
        fullname = fullname_match.group(1).strip() if fullname_match else username
        
        bio_match = re.search(r'<div class="profile-description">\s*(.*?)\s*</div>', html, re.DOTALL)
        bio = clean_html(bio_match.group(1)) if bio_match else ""
        
        # Parse posts
        post_boxes = re.findall(r'<div class="box-photo">(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
        posts = []
        
        for box in post_boxes:
            shortcode_match = re.search(r'href="https://www.picuki.com/media/([^"]+)"', box)
            desc_match = re.search(r'<p class="photo-description">\s*(.*?)\s*</p>', box, re.DOTALL)
            likes_match = re.search(r'<div class="likes">.*?([\d,km.]+)', box, re.DOTALL | re.IGNORECASE)
            comments_match = re.search(r'<div class="comments">.*?([\d,km.]+)', box, re.DOTALL | re.IGNORECASE)
            time_match = re.search(r'<div class="time">\s*([^<]+)\s*</div>', box)
            
            if shortcode_match:
                shortcode = shortcode_match.group(1).strip()
                desc = clean_html(desc_match.group(1)) if desc_match else ""
                likes = likes_match.group(1).strip() if likes_match else "0"
                comments = comments_match.group(1).strip() if comments_match else "0"
                post_time = time_match.group(1).strip() if time_match else ""
                
                posts.append({
                    "shortcode": shortcode,
                    "caption": desc,
                    "likes": likes,
                    "comments": comments,
                    "time": post_time
                })
                
        return {
            "username": extracted_username,
            "full_name": fullname,
            "biography": bio,
            "posts": posts
        }
    except Exception as e:
        print(f"[INSTAGRAM-ERROR] Ошибка при парсинге профиля с Picuki: {e}")
        return None

def scrape_imgsed_profile(username):
    """Fallback profile scraper using Imgsed."""
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = f"https://imgsed.com/profile/{username}"
    
    cmd = [
        "curl.exe", "-s", "-L",
        "-A", ua,
        "-H", "Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = result.stdout
        
        if not html or "profile-name" not in html:
            return None
            
        # Parse profile details
        username_match = re.search(r'<div class="profile-name">[^@]*@([^<]+)</div>', html)
        extracted_username = username_match.group(1).strip() if username_match else username
        
        fullname_match = re.search(r'<h1 class="profile-title">([^<]+)</h1>', html)
        fullname = fullname_match.group(1).strip() if fullname_match else username
        
        bio_match = re.search(r'<div class="profile-description">\s*(.*?)\s*</div>', html, re.DOTALL)
        bio = clean_html(bio_match.group(1)) if bio_match else ""
        
        # Parse posts (Imgsed shares a very similar HTML template to Picuki)
        post_boxes = re.findall(r'<div class="box-photo">(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
        posts = []
        
        for box in post_boxes:
            shortcode_match = re.search(r'href="https://imgsed.com/media/([^"]+)"', box) or re.search(r'href="https://www.picuki.com/media/([^"]+)"', box)
            desc_match = re.search(r'<p class="photo-description">\s*(.*?)\s*</p>', box, re.DOTALL)
            likes_match = re.search(r'<div class="likes">.*?([\d,km.]+)', box, re.DOTALL | re.IGNORECASE)
            comments_match = re.search(r'<div class="comments">.*?([\d,km.]+)', box, re.DOTALL | re.IGNORECASE)
            time_match = re.search(r'<div class="time">\s*([^<]+)\s*</div>', box)
            
            if shortcode_match:
                shortcode = shortcode_match.group(1).strip()
                desc = clean_html(desc_match.group(1)) if desc_match else ""
                likes = likes_match.group(1).strip() if likes_match else "0"
                comments = comments_match.group(1).strip() if comments_match else "0"
                post_time = time_match.group(1).strip() if time_match else ""
                
                posts.append({
                    "shortcode": shortcode,
                    "caption": desc,
                    "likes": likes,
                    "comments": comments,
                    "time": post_time
                })
                
        return {
            "username": extracted_username,
            "full_name": fullname,
            "biography": bio,
            "posts": posts
        }
    except Exception as e:
        print(f"[INSTAGRAM-ERROR] Ошибка при парсинге профиля с Imgsed: {e}")
        return None

def scrape_picuki_media(shortcode):
    """Scrapes a specific post from Picuki."""
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = f"https://www.picuki.com/media/{shortcode}"
    
    cmd = [
        "curl.exe", "-s", "-L",
        "-A", ua,
        "-H", "Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = result.stdout
        
        if not html or "post-description" not in html:
            return None
            
        author_match = re.search(r'<div class="profile-name">[^@]*@([^<]+)</div>', html)
        author = author_match.group(1).strip() if author_match else "Unknown"
        
        desc_match = re.search(r'<div class="post-description">\s*(.*?)\s*</div>', html, re.DOTALL)
        description = clean_html(desc_match.group(1)) if desc_match else ""
        
        likes_match = re.search(r'<span class="likes-count">([^<]+)</span>', html)
        likes = likes_match.group(1).strip() if likes_match else "0"
        
        comments_match = re.search(r'<span class="comments-count">([^<]+)</span>', html)
        comments = comments_match.group(1).strip() if comments_match else "0"
        
        return {
            "shortcode": shortcode,
            "author": author,
            "caption": description,
            "likes": likes,
            "comments": comments
        }
    except Exception as e:
        print(f"[INSTAGRAM-ERROR] Ошибка при парсинге поста с Picuki: {e}")
        return None

def scrape_imgsed_media(shortcode):
    """Fallback post scraper using Imgsed."""
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = f"https://imgsed.com/media/{shortcode}"
    
    cmd = [
        "curl.exe", "-s", "-L",
        "-A", ua,
        "-H", "Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        html = result.stdout
        
        if not html or "post-description" not in html:
            return None
            
        author_match = re.search(r'<div class="profile-name">[^@]*@([^<]+)</div>', html)
        author = author_match.group(1).strip() if author_match else "Unknown"
        
        desc_match = re.search(r'<div class="post-description">\s*(.*?)\s*</div>', html, re.DOTALL)
        description = clean_html(desc_match.group(1)) if desc_match else ""
        
        likes_match = re.search(r'<span class="likes-count">([^<]+)</span>', html)
        likes = likes_match.group(1).strip() if likes_match else "0"
        
        comments_match = re.search(r'<span class="comments-count">([^<]+)</span>', html)
        comments = comments_match.group(1).strip() if comments_match else "0"
        
        return {
            "shortcode": shortcode,
            "author": author,
            "caption": description,
            "likes": likes,
            "comments": comments
        }
    except Exception as e:
        print(f"[INSTAGRAM-ERROR] Ошибка при парсинге поста с Imgsed: {e}")
        return None

def get_instagram_content(url):
    """
    Primary interface to scrape Instagram profile or post content.
    Automatically parses the URL to decide whether to fetch profile or post.
    Supports failover between Picuki and Imgsed.
    """
    import time
    print(f"[INSTAGRAM] Анализ URL: {url}")
    print("[INSTAGRAM] Пауза 2.5 секунды для обхода блокировок...")
    time.sleep(2.5)
    
    # 1. Detect if it's a post/reel or a profile
    # Common Instagram URL structures:
    # - Post: https://www.instagram.com/p/C6bC5H7R5e3/
    # - Reel: https://www.instagram.com/reel/C7c5T7xR2e1/
    # - Profile: https://www.instagram.com/nasa/
    
    is_post = "/p/" in url or "/reel/" in url
    
    # Clean URL and extract handles
    url_cleaned = url.split("?")[0].rstrip("/")
    parts = url_cleaned.split("/")
    
    if is_post:
        shortcode = parts[-1]
        print(f"[INSTAGRAM] Обнаружен пост/рилс. Код публикации: {shortcode}")
        
        # Try Picuki first
        data = scrape_picuki_media(shortcode)
        if not data:
            print("[INSTAGRAM] Picuki вернул пустой результат. Пробуем зеркало Imgsed...")
            data = scrape_imgsed_media(shortcode)
            
        if not data:
            print("[INSTAGRAM-ERROR] Не удалось загрузить публикацию из доступных источников.")
            return None
            
        # Format structured text response
        structured_text = f"""[INSTAGRAM POST]
Автор: @{data['author']}
Ссылка: https://www.instagram.com/p/{data['shortcode']}/
Статистика: {data['likes']} лайков, {data['comments']} комментариев

Текст публикации:
--------------------------------------------------
{data['caption']}
--------------------------------------------------
"""
        return structured_text
    else:
        # Profile mode
        username = parts[-1]
        print(f"[INSTAGRAM] Обнаружен профиль. Пользователь: @{username}")
        
        # Try Picuki first
        data = scrape_picuki_profile(username)
        if not data:
            print("[INSTAGRAM] Picuki вернул пустой результат. Пробуем зеркало Imgsed...")
            data = scrape_imgsed_profile(username)
            
        if not data:
            print("[INSTAGRAM-ERROR] Не удалось загрузить профиль из доступных источников.")
            return None
            
        # Format structured text response
        posts_text = ""
        for idx, post in enumerate(data['posts']):
            posts_text += f"""
[{idx+1}] Публикация: https://www.instagram.com/p/{post['shortcode']}/
Время публикации: {post['time']}
Статистика: {post['likes']} лайков, {post['comments']} комментариев
Текст:
{post['caption']}
--------------------------------------------------
"""
            
        structured_text = f"""[INSTAGRAM PROFILE]
Пользователь: @{data['username']} ({data['full_name']})
Ссылка: https://www.instagram.com/{data['username']}/
Биография: {data['biography']}

Последние {len(data['posts'])} публикаций:
==================================================
{posts_text}
==================================================
"""
        return structured_text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python instagram_extractor.py <URL>")
        sys.exit(1)
        
    url_source = sys.argv[1]
    res = get_instagram_content(url_source)
    if res:
        print("\n--- Спарсенный контент ---")
        print(res[:1000] + "\n..." if len(res) > 1000 else res)
    else:
        print("\n[ФЕЙЛ] Не удалось извлечь контент.")
