import os
import sys
import subprocess
import time

# Reconfigure stdout/stderr to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_script(script_path, args=[]):
    cmd = [sys.executable, script_path] + args
    print(f"\n==================================================")
    print(f"[RUNNER] Запуск: {' '.join(cmd)}")
    print(f"==================================================")
    
    # We run with real-time stdout redirection to console
    res = subprocess.run(cmd, text=True, errors="ignore")
    if res.returncode != 0:
        print(f"[RUNNER-ERROR] Скрипт {script_path} завершился с ошибкой (код: {res.returncode})")
        return False
    return True

def main():
    print("🚀 Запуск ПОЛНОГО автономного конвейера (100 видео и 100 shorts) по теме 'Заработок с ИИ'...")
    
    # Шаг 1. Переопределяем параметры запуска в youtube_bulk_crawler.py для 100 видео и 100 shorts
    # Вместо редактирования файла мы можем передать аргументы командной строки или временно переписать вызов.
    # Но для максимальной простоты мы можем запустить сборщик с флагами, если обновим его, либо запустить напрямую.
    # Давайте сделаем так: запустим с аргументами, если мы доработаем youtube_bulk_crawler.py.
    # Или мы можем временно пропатчить вызов в youtube_bulk_crawler.py.
    # Давайте обновим вызов в самом youtube_bulk_crawler.py, чтобы он принимал аргументы из командной строки!
    
    crawler_script = os.path.join("src", "knowledge_extractor", "youtube_bulk_crawler.py")
    orchestrator_script = os.path.join("src", "knowledge_extractor", "notebooklm_orchestrator.py")
    generator_script = os.path.join("src", "knowledge_extractor", "obsidian_skills_generator.py")
    
    # Запускаем сборщик 100 видео и 100 shorts
    # Мы передадим аргументы --max-videos 100 --max-shorts 100
    if not run_script(crawler_script, ["--max-videos", "100", "--max-shorts", "100"]):
        sys.exit(1)
        
    # Запускаем импорт и RAG-синтез в NotebookLM
    if not run_script(orchestrator_script):
        sys.exit(1)
        
    # Запускаем нарезку заметок Obsidian и генерацию .skills
    if not run_script(generator_script):
        sys.exit(1)
        
    print("\n🎉 [SUCCESS] Полный локальный цикл на 100 видео и 100 shorts успешно выполнен!")
    print("Все новые заметки синхронизированы в Obsidian Vault на диске G:\\ и локально.")

if __name__ == "__main__":
    main()
