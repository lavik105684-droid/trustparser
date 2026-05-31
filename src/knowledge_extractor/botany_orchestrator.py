import os
import sys
import subprocess
import json
import re

# Reconfigure stdout/stderr to UTF-8 to prevent any Windows encoding crashes
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

NLM_PATH = r"C:\Users\lavik\AppData\Roaming\Python\Python314\Scripts\nlm.exe"
REGISTRY_FILE = os.path.join("scratch", "botany_registry.json")

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

def get_or_create_notebook(title="Botany_Home_Grow_Vault"):
    print(f"[ORCHESTRATOR] Поиск блокнота '{title}'...")
    list_out = run_nlm(["notebook", "list", "--json"])
    
    if list_out:
        try:
            notebooks = json.loads(list_out)
            for nb in notebooks:
                if nb.get("title") == title or nb.get("name") == title:
                    nb_id = nb.get("id")
                    print(f"[ORCHESTRATOR] Найден существующий ботанический блокнот: {title} (ID: {nb_id})")
                    return nb_id
        except Exception:
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
        match = re.search(r'\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b', create_out)
        if match:
            nb_id = match.group(1)
            print(f"[ORCHESTRATOR] Блокнот успешно создан (ID: {nb_id})")
            return nb_id
            
    print("[ORCHESTRATOR-ERROR] Не удалось получить или создать ботанический блокнот.")
    return None

def upload_registry_sources(nb_id):
    if not os.path.exists(REGISTRY_FILE):
        print(f"[ORCHESTRATOR-ERROR] Файл реестра {REGISTRY_FILE} не существует.")
        return False
        
    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as r_f:
            registry = json.load(r_f)
    except Exception as e:
        print(f"[ORCHESTRATOR-ERROR] Ошибка чтения реестра: {e}")
        return False
        
    if not registry:
        print("[ORCHESTRATOR] В реестре нет записей для импорта.")
        return True
        
    # List current sources to prevent duplicates
    sources_out = run_nlm(["source", "list", nb_id, "--json"])
    existing_titles = []
    if sources_out:
        try:
            sources = json.loads(sources_out)
            existing_titles = [s.get("title", "").lower() for s in sources]
        except Exception:
            pass
            
    print(f"[ORCHESTRATOR] Найдено {len(registry)} роликов в реестре. Начинаем импорт в Botany Vault...")
    
    success_count = 0
    for idx, (vid_id, item) in enumerate(registry.items()):
        url = item.get("url")
        title = item.get("title")
        
        if title.lower() in existing_titles:
            print(f"[{idx+1}/{len(registry)}] [ПРОПУСК] Источник '{title}' уже импортирован.")
            continue
            
        print(f"[{idx+1}/{len(registry)}] Импорт YouTube: {title} ({url})...")
        res = run_nlm(["source", "add", nb_id, "--youtube", url, "--wait"])
        if res and ("✓" in res or "Success" in res or "Added" in res or "ready" in res):
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

def run_botany_rag_synthesis(nb_id):
    print("\n[ORCHESTRATOR] Запуск ботанического RAG-синтеза в NotebookLM...")
    
    queries = {
        "devices": (
            "Найди и составь исчерпывающий справочник ВСЕХ приборов, приспособлений, датчиков влажности, систем автоматического полива, "
            "фитоламп досветки (светодиодных, PPFD/люксы, спектры), упомянутых в источниках. "
            "Для каждого прибора укажи категорию, его точную роль в уходе, оптимальные параметры настройки и лайфхаки использования. "
            "Оформи каждый прибор под заголовком '#### [DEVICE] Название' для последующего автоматического парсинга."
        ),
        "chemistry": (
            "Собери и подробно распиши всю химию, удобрения, фунгициды, инсектициды, стимуляторы роста (НВ-101, цитокининовая паста), "
            "составы почвосмесей (вермикулит, перлит, лечуза-пон, кокос) и точные пропорции/соотношения NPK для разных фаз развития, упомянутые в источниках. "
            "Оформи каждое вещество/рецепт под заголовком '#### [CHEMISTRY] Название' для последующего автоматического парсинга."
        ),
        "plants": (
            "Выдели подробные практические руководства по выращиванию конкретных декоративно-лиственных (Аллоказии, Монстеры) "
            "и плодоносящих культур (лимоны, инжир, клубника), упомянутые в источниках. "
            "Опиши температурный режим, полив, размножение, частые проблемы (корневая гниль, паразиты) и пошаговые мануалы ухода. "
            "Оформи каждую культуру под заголовком '#### [PLANT] Название' для последующего автоматического парсинга."
        ),
        "index": (
            "Составь глобальный структурированный путеводитель по домашнему растениеводству и классификатор по всем темам, "
            "затронутым во всех источниках. Сгруппируй выводы по категориям (Свет, Полив, Грунты, Защита) и перечисли ключевые рекомендации."
        )
    }
    
    success = True
    for key, question in queries.items():
        output_file = os.path.join("scratch", f"botany_synthesis_{key}.md")
        print(f"[ORCHESTRATOR] Выполнение RAG-запроса '{key}'...")
        
        query_out = run_nlm(["notebook", "query", nb_id, question, "--timeout", "300"])
        if query_out:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(query_out)
            print(f"[ORCHESTRATOR-SUCCESS] Отчет '{key}' успешно сохранен: {output_file}")
        else:
            print(f"[ORCHESTRATOR-ERROR] Не удалось получить RAG-отчет '{key}' от NotebookLM.")
            success = False
            
    return success

def main():
    nb_id = get_or_create_notebook()
    if not nb_id:
        print("[ORCHESTRATOR] Не удалось продолжить: отсутствует Botany Notebook ID.")
        sys.exit(1)
        
    upload_registry_sources(nb_id)
    run_botany_rag_synthesis(nb_id)
    print("\n[ORCHESTRATOR] Все ботанические этапы NotebookLM успешно завершены!")

if __name__ == "__main__":
    main()
