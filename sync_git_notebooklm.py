import os
import sys
import subprocess

# Reconfigure stdout/stderr to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd):
    print(f"\n[SYNC-RUNNER] Выполнение: {' '.join(cmd)}")
    res = subprocess.run(cmd, text=True, errors="ignore")
    return res.returncode == 0

def main():
    print("🔄 Запуск локальной синхронизации с Git-репозиторием и NotebookLM...")
    
    # Шаг 1. Делаем git pull для стягивания ссылок, собранных GitHub Actions / Jules
    print("\n[1/4] Обновление реестра ссылок из Git...")
    if not run_cmd(["git", "pull"]):
        print("[WARNING] Не удалось выполнить git pull. Возможно, удаленный репозиторий еще не настроен или нет изменений. Продолжаем со встроенным реестром...")

    # Шаг 2. Запуск оркестратора для загрузки новых ссылок в NotebookLM и RAG-синтеза
    print("\n[2/4] Загрузка новых источников в NotebookLM и выполнение RAG-синтеза...")
    orchestrator_script = os.path.join("src", "knowledge_extractor", "notebooklm_orchestrator.py")
    if not run_cmd([sys.executable, orchestrator_script]):
        print("[ERROR] Сбой на этапе NotebookLM-анализа.")
        sys.exit(1)

    # Шаг 3. Запуск генератора для нарезки Markdown-заметок и .skills файлов
    print("\n[3/4] Генерация заметок Obsidian и файлов .skills...")
    generator_script = os.path.join("src", "knowledge_extractor", "obsidian_skills_generator.py")
    if not run_cmd([sys.executable, generator_script]):
        print("[ERROR] Сбой на этапе генерации Obsidian-заметок.")
        sys.exit(1)
        
    print("\n🎉 [SUCCESS] Синхронизация успешно завершена! Все новые ИИ-знания в вашем Obsidian Vault!")

if __name__ == "__main__":
    main()
