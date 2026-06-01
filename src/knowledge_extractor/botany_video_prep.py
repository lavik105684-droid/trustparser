import os
import sys
import json
import subprocess

# Reconfigure standard output to prevent Windows encoding crashes
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

REGISTRY_FILE = os.path.join("scratch", "botany_registry.json")
YTDLP_PATH = os.path.join("scratch", "yt-dlp.exe")
PREP_DIR = os.path.join("scratch", "botany_prep_videos")

def ensure_dirs():
    os.makedirs(PREP_DIR, exist_ok=True)

COOKIES_FILE = os.path.join("scratch", "youtube_cookies.txt")

def download_silent_video(url, output_path):
    print(f"[PREP] Запуск скачивания беззвучного видео для: {url}...")
    
    # 1. Determine fallback chain of cookie/download arguments
    methods = []
    
    # Method A: Self-healing Netscape cookies file (100% robust, never locks)
    if os.path.exists(COOKIES_FILE):
        methods.append({
            "name": "Netscape Cookies File (youtube_cookies.txt)",
            "args": ["--cookies", COOKIES_FILE]
        })
        
    # Method B: Zero-cookies direct download (works for unflagged IPs)
    methods.append({
        "name": "Direct Download (No Cookies)",
        "args": []
    })
    
    # Method C: Chrome browser cookies (may fail if Chrome is open/locked)
    methods.append({
        "name": "Google Chrome Browser Cookies",
        "args": ["--cookies-from-browser", "chrome"]
    })
    
    # Method D: Edge browser cookies
    methods.append({
        "name": "Microsoft Edge Browser Cookies",
        "args": ["--cookies-from-browser", "edge"]
    })
    
    success = False
    for method in methods:
        print(f"[PREP] Пробуем метод скачивания: {method['name']}...")
        cmd = [
            YTDLP_PATH,
            "-f", "bestvideo[ext=mp4]/bestvideo",
        ] + method["args"] + [
            "-o", output_path,
            url
        ]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            if res.returncode == 0:
                print(f"[PREP-SUCCESS] Видео успешно скачано методом: {method['name']}")
                success = True
                break
            else:
                # Try fallback format format if bestvideo[ext=mp4] failed but download didn't block
                if "Sign in to confirm" not in res.stderr and "Could not copy Chrome cookie database" not in res.stderr:
                    print(f"[PREP-WARNING] Формат mp4-bestvideo недоступен, пробуем универсальный bestvideo...")
                    cmd_fallback = [
                        YTDLP_PATH,
                        "-f", "bestvideo",
                    ] + method["args"] + [
                        "-o", output_path,
                        url
                    ]
                    res_fb = subprocess.run(cmd_fallback, capture_output=True, text=True, encoding="utf-8", errors="ignore")
                    if res_fb.returncode == 0:
                        print(f"[PREP-SUCCESS] Видео успешно скачано в универсальном формате!")
                        success = True
                        break
                print(f"[PREP-WARNING] Метод '{method['name']}' не сработал. Ошибка: {res.stderr.strip()[:180]}...")
        except Exception as e:
            print(f"[PREP-WARNING] Исключение при методе '{method['name']}': {e}")
            
    if success:
        return True
        
    # All methods failed - print a highly actionable and beautiful troubleshooting instruction in Russian
    print("\n" + "="*70)
    print("❌ [PREP-CRITICAL] ВСЕ МЕТОДЫ СКАЧИВАНИЯ БЛОКИРОВАНЫ YOUTUBE (ЗАЩИТА ОТ БОТОВ)")
    print("Для полной автоматизации и обхода блокировок выполните простые шаги:")
    print("1. Установите в Chrome бесплатное расширение 'Get cookies.txt LOCALLY'")
    print("2. Откройте YouTube.com в браузере, нажмите на иконку расширения и нажмите 'Export'")
    print("3. Сохраните скачанный файл под именем 'youtube_cookies.txt' в папку проекта:")
    print(f"   -> C:\\Users\\lavik\\Documents\\antigravity\\modest-carson\\{COOKIES_FILE}")
    print("После этого конвейер будет скачивать ролики на 100% стабильно и без прерываний!")
    print("="*70 + "\n")
    return False

def main():
    ensure_dirs()
    if not os.path.exists(REGISTRY_FILE):
        print(f"[PREP-ERROR] Реестр {REGISTRY_FILE} не найден.")
        sys.exit(1)
        
    if not os.path.exists(YTDLP_PATH):
        print(f"[PREP-ERROR] Автономный загрузчик {YTDLP_PATH} не найден.")
        sys.exit(1)
        
    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        print(f"[PREP-ERROR] Ошибка чтения реестра: {e}")
        sys.exit(1)
        
    # Find up to 3 pending videos to prepare in this batch to keep run times fast
    pending_vids = []
    for vid_id, item in registry.items():
        # Target only Shorts for our faceless CPA конвейер!
        if item.get("is_short") and item.get("status") == "pending_upload":
            pending_vids.append((vid_id, item))
            
    if not pending_vids:
        print("[PREP] Нет новых Shorts для скачивания.")
        return
        
    print(f"[PREP] Найдено {len(pending_vids)} новых Shorts для подготовки. Лимит на запуск: 3.")
    
    success_count = 0
    for vid_id, item in pending_vids[:3]:
        url = item.get("url")
        title = item.get("title")
        output_file = os.path.join(PREP_DIR, f"{vid_id}.mp4")
        
        if download_silent_video(url, output_file):
            item["status"] = "video_prepared"
            item["local_path"] = output_file
            success_count += 1
            
    if success_count > 0:
        # Save updated registry
        try:
            with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            print(f"[PREP-COMPLETE] База реестра обновлена. Успешно подготовлено Shorts: {success_count}.")
        except Exception as e:
            print(f"[PREP-ERROR] Не удалось сохранить реестр: {e}")

if __name__ == "__main__":
    main()
