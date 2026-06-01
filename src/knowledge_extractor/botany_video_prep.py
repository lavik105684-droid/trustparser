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

def download_silent_video(url, output_path):
    print(f"[PREP] Запуск скачивания беззвучного видео для: {url}...")
    # Pass -f "bestvideo[ext=mp4]/bestvideo" to download ONLY video stream (silent)
    cmd = [
        YTDLP_PATH,
        "-f", "bestvideo[ext=mp4]/bestvideo",
        "-o", output_path,
        url
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if res.returncode == 0:
            print(f"[PREP-SUCCESS] Видео сохранено: {output_path}")
            return True
        else:
            # Fallback if bestvideo format is not available in mp4, download general best video
            print(f"[PREP-WARNING] Не удалось скачать mp4-bestvideo, пробуем универсальный bestvideo...")
            cmd_fallback = [YTDLP_PATH, "-f", "bestvideo", "-o", output_path, url]
            res_fb = subprocess.run(cmd_fallback, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            if res_fb.returncode == 0:
                print(f"[PREP-SUCCESS] Видео (универсальный формат) сохранено: {output_path}")
                return True
            print(f"[PREP-ERROR] Ошибка скачивания (код {res_fb.returncode}): {res_fb.stderr}")
            return False
    except Exception as e:
        print(f"[PREP-ERROR] Исключение при запуске yt-dlp: {e}")
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
