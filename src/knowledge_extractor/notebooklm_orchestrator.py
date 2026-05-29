import os
import sys
import subprocess
import json
import re

# Reconfigure stdout/stderr to UTF-8 to prevent any Windows encoding crashes with emojis or Russian text
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

NLM_PATH = r"C:\Users\lavik\AppData\Roaming\Python\Python314\Scripts\nlm.exe"
CACHE_DIR = os.path.join("scratch", "yt_cache")
SYNTHESIS_FILE = os.path.join("scratch", "notebooklm_synthesis.md")

def run_nlm(args):
    """Runs nlm CLI command and returns stdout."""
    cmd = [NLM_PATH] + args
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if res.returncode != 0:
            print(f"[NLM-ERROR] Command failed: {' '.join(cmd)}")
            print(f"[NLM-ERROR] Stderr: {res.stderr}")
            return None
        return res.stdout.strip()
    except Exception as e:
        print(f"[NLM-ERROR] Exception running {' '.join(cmd)}: {e}")
        return None

def get_or_create_notebook(title="YouTube_AI_Factory_Vault"):
    print(f"[ORCHESTRATOR] Поиск блокнота '{title}'...")
    # List notebooks
    list_out = run_nlm(["notebook", "list", "--json"])
    
    if list_out:
        try:
            notebooks = json.loads(list_out)
            for nb in notebooks:
                if nb.get("title") == title or nb.get("name") == title:
                    nb_id = nb.get("id")
                    print(f"[ORCHESTRATOR] Найден существующий блокнот: {title} (ID: {nb_id})")
                    return nb_id
        except Exception:
            # Fallback to text parsing if json fails
            for line in list_out.splitlines():
                if title in line:
                    match = re.search(r'\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b', line)
                    if match:
                        nb_id = match.group(1)
                        print(f"[ORCHESTRATOR] Найдено совпадение в выводе: {title} (ID: {nb_id})")
                        return nb_id
                        
    # Not found, create it
    print(f"[ORCHESTRATOR] Блокнот не найден. Создание нового '{title}'...")
    create_out = run_nlm(["notebook", "create", title])
    if create_out:
        # Extract UUID from output
        match = re.search(r'\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b', create_out)
        if match:
            nb_id = match.group(1)
            print(f"[ORCHESTRATOR] Блокнот успешно создан (ID: {nb_id})")
            return nb_id
            
    # Try listing again as last fallback
    list_out = run_nlm(["notebook", "list"])
    if list_out:
        for line in list_out.splitlines():
            if title in line:
                match = re.search(r'\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b', line)
                if match:
                    return match.group(1)
                    
    print("[ORCHESTRATOR-ERROR] Не удалось получить или создать блокнот.")
    return None

def upload_cache_files(nb_id):
    registry_path = os.path.join("scratch", "yt_registry.json")
    if not os.path.exists(registry_path):
        print(f"[ORCHESTRATOR-ERROR] Файл реестра {registry_path} не существует.")
        return False
        
    try:
        with open(registry_path, "r", encoding="utf-8") as r_f:
            registry = json.load(r_f)
    except Exception as e:
        print(f"[ORCHESTRATOR-ERROR] Ошибка чтения реестра: {e}")
        return False
        
    if not registry:
        print("[ORCHESTRATOR] В реестре нет записей для импорта.")
        return True
        
    # List current sources in notebook to prevent duplicates
    sources_out = run_nlm(["source", "list", nb_id, "--json"])
    existing_titles = []
    if sources_out:
        try:
            sources = json.loads(sources_out)
            existing_titles = [s.get("title", "").lower() for s in sources]
        except Exception:
            pass
            
    print(f"[ORCHESTRATOR] Найдено {len(registry)} роликов в реестре. Начинаем импорт в NotebookLM...")
    
    success_count = 0
    for idx, (vid_id, item) in enumerate(registry.items()):
        url = item.get("url")
        title = item.get("title")
        
        # Check if already present
        if title.lower() in existing_titles:
            print(f"[{idx+1}/{len(registry)}] [ПРОПУСК] Источник '{title}' уже импортирован.")
            continue
            
        print(f"[{idx+1}/{len(registry)}] Импорт YouTube: {title} ({url})...")
        # Upload YouTube URL directly and wait for cloud extraction (without --debug option)
        res = run_nlm(["source", "add", nb_id, "--youtube", url, "--wait"])
        if res and ("✓" in res or "Success" in res or "Added source" in res or "ready" in res):
            success_count += 1
            print(f"[УСПЕХ] Ролик {title} успешно импортирован.")
        else:
            print(f"[ВАРНИНГ] Прямой импорт с --wait завис или выдал предупреждение. Пробуем асинхронно...")
            res_async = run_nlm(["source", "add", nb_id, "--youtube", url])
            if res_async:
                success_count += 1
                print(f"[УСПЕХ] Асинхронно отправлен на импорт: {title}")
            else:
                print(f"[ОШИБКА] Не удалось загрузить {title}")
                
    print(f"[ORCHESTRATOR] Импорт YouTube-источников завершен. Загружено новых: {success_count} штук.")
    return True

def run_rag_synthesis(nb_id):
    print("\n[ORCHESTRATOR] Запуск глобального RAG-синтеза в NotebookLM...")
    
    question = (
        "Проанализируй все загруженные транскрипты. Выдели 20 ключевых практических ИИ-инструментов, "
        "пошаговые мануалы по локальной установке n8n в Docker, n8n-схемы для парсинга и генерации контента, "
        "а также рабочие схемы монетизации ИИ (от поддержки бизнеса до CPA и блогинга). "
        "Сформируй единый детальный, красивый markdown-отчет на русском языке с четкими заголовками, "
        "листингами кода, конфигами и тегами, связывающими темы между собой."
    )
    
    # Run the query (timeout 300 seconds for massive notebook cross-analysis)
    query_out = run_nlm(["notebook", "query", nb_id, question, "--timeout", "300"])
    
    if query_out:
        with open(SYNTHESIS_FILE, "w", encoding="utf-8") as f:
            f.write(query_out)
        print(f"[ORCHESTRATOR-SUCCESS] Глобальный RAG-отчет успешно сохранен: {SYNTHESIS_FILE}")
        return True
    else:
        print("[ORCHESTRATOR-ERROR] Не удалось получить RAG-синтез от NotebookLM.")
        return False

def main():
    nb_id = get_or_create_notebook()
    if not nb_id:
        print("[ORCHESTRATOR] Не удалось продолжить: отсутствует Notebook ID.")
        sys.exit(1)
        
    upload_cache_files(nb_id)
    run_rag_synthesis(nb_id)
    print("\n[ORCHESTRATOR] Все этапы NotebookLM успешно завершены!")

if __name__ == "__main__":
    main()
