import urllib.request
import urllib.error
import json
import os

def load_env(env_path=".env"):
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def test_instagram_connection(target_username="nasa"):
    load_env()
    
    session_id = os.environ.get("INSTAGRAM_SESSION_ID", "").strip()
    user_id = os.environ.get("INSTAGRAM_USER_ID", "").strip()
    csrf_token = os.environ.get("INSTAGRAM_CSRF_TOKEN", "").strip()
    
    if not session_id or not user_id or not csrf_token:
        print("[ОШИБКА] Учетные данные Instagram не найдены в .env!")
        return False
        
    print(f"[INSTAGRAM] Запуск теста подключения для профиля: @{target_username}...")
    
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={target_username}"
    
    cookie_str = f"sessionid={session_id}; ds_user_id={user_id}; csrftoken={csrf_token}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459", # Mandatory Instagram Web App ID
        "X-CSRFToken": csrf_token,
        "Cookie": cookie_str,
        "Referer": "https://www.instagram.com/"
    }
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode("utf-8"))
            
        user_info = res.get("data", {}).get("user", {})
        if user_info:
            print("\n[УСПЕХ] Успешное подключение к Instagram API!")
            print("-------------------------------------------------------")
            print("Аккаунт:", user_info.get("username"))
            print("Имя:", user_info.get("full_name"))
            print("Биография:", user_info.get("biography"))
            print("Подписчиков:", user_info.get("edge_followed_by", {}).get("count"))
            print("Количество постов:", user_info.get("edge_owner_to_timeline_media", {}).get("count"))
            
            # Print a preview of the first post
            edges = user_info.get("edge_owner_to_timeline_media", {}).get("edges", [])
            if edges:
                first_post = edges[0].get("node", {})
                caption = first_post.get("edge_media_to_caption", {}).get("edges", [])
                caption_text = caption[0].get("node", {}).get("text", "") if caption else "Нет текста"
                print("\nПоследний пост:")
                print(f"- Текст: {caption_text[:150]}...")
                print(f"- Ссылка: https://www.instagram.com/p/{first_post.get('shortcode')}/")
            print("-------------------------------------------------------")
            return True
        else:
            print("[ОШИБКА] API вернуло пустые данные о пользователе.")
            return False
            
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        print(f"[ОШИБКА] Instagram API вернул HTTP код {e.code}: {e.reason}")
        print("Ответ сервера:", err_body[:300])
        return False
    except Exception as e:
        print(f"[ОШИБКА] Не удалось выполнить запрос: {e}")
        return False

if __name__ == "__main__":
    test_instagram_connection()
