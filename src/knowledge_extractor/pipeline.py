import os
import sys
import json
import urllib.request
import urllib.error
import re
from youtube_extractor import get_youtube_transcript
from web_extractor import scrape_web_article
from instagram_extractor import get_instagram_content

# Custom minimal .env parser to maintain zero dependency footprint
def load_env(env_path=".env"):
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def run_extraction_pipeline(url_source):
    load_env()
    
    # Check if the input is a direct URL or a search query
    is_url = url_source.startswith("http://") or url_source.startswith("https://") or url_source.startswith("www.")
    
    if not is_url:
        print(f"[PIPELINE] Входные данные распознаны как поисковый запрос: '{url_source}'")
        from discovery import discover_resources
        
        # 1. Discover resources
        discovered = discover_resources(url_source)
        
        # 2. Select the best match
        best_match_url = None
        best_match_title = None
        
        # Priority: Web articles -> YouTube videos -> Instagram
        if discovered["web"]:
            best_match_url = discovered["web"][0]["url"]
            best_match_title = discovered["web"][0]["title"]
        elif discovered["youtube"]:
            best_match_url = discovered["youtube"][0]["url"]
            best_match_title = discovered["youtube"][0]["title"]
        elif discovered["instagram"]:
            best_match_url = discovered["instagram"][0]["url"]
            best_match_title = discovered["instagram"][0]["title"]
            
        # 3. Generate Obsidian Search Index file
        obsidian_vault = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
        if obsidian_vault:
            kb_dir = os.path.join(os.path.normpath(obsidian_vault), "knowledge_base")
        else:
            kb_dir = "knowledge_base"
            
        os.makedirs(kb_dir, exist_ok=True)
        
        # Make a URL friendly slug
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', url_source.lower()).strip('_')
        index_file_path = os.path.join(kb_dir, f"search_{slug}.md")
        
        # Build search index content
        index_content = f"""# Поисковый индекс: "{url_source}"

Этот индексный файл содержит результаты автоматического поиска по вашему запросу. Вы можете запустить детальный разбор любого из этих источников, выполнив соответствующую команду в терминале.

## 🎯 Автоматически выбранный лучший источник
**{best_match_title or "Не найдено"}**
- Ссылка: {best_match_url or "Нет"}
- Статус: *Успешно импортирован в базу знаний*

---

## 📹 Релевантные видеоролики на YouTube
"""
        for idx, yt in enumerate(discovered["youtube"]):
            index_content += f"- **[{yt['title']}]({yt['url']})** (ID: `{yt['id']}`)\n  *Команда для разбора:* `python src/knowledge_extractor/pipeline.py {yt['url']}`\n"
            
        index_content += "\n## 📄 Полезные статьи и документация\n"
        for idx, web in enumerate(discovered["web"]):
            index_content += f"- **[{web['title']}]({web['url']})**\n  *Команда для разбора:* `python src/knowledge_extractor/pipeline.py {web['url']}`\n"
            
        index_content += "\n## 📸 Профили и материалы Instagram\n"
        for idx, ig in enumerate(discovered["instagram"]):
            index_content += f"- **{ig['title']}** (Ссылка: {ig['url']})\n  *Команда для разбора:* `python src/knowledge_extractor/pipeline.py {ig['url']}`\n"
            
        with open(index_file_path, "w", encoding="utf-8") as index_f:
            index_f.write(index_content)
        print(f"[PIPELINE-SUCCESS] Создан поисковый индекс в Obsidian: {index_file_path}")
        
        if not best_match_url:
            print("[PIPELINE-ERROR] Не удалось найти ни одного подходящего источника по запросу.")
            return False
            
        print(f"[PIPELINE] Выбран лучший источник: '{best_match_title}' -> {best_match_url}")
        # Proceed with extracting and structuring the best match!
        url_source = best_match_url

    # 1. Detect Source Type & Extract Text
    is_youtube = "youtube.com" in url_source or "youtu.be" in url_source or len(url_source) == 11
    is_instagram = "instagram.com" in url_source
    
    if is_youtube:
        print("[PIPELINE] Обнаружен источник: YouTube")
        raw_text = get_youtube_transcript(url_source)
    elif is_instagram:
        print("[PIPELINE] Обнаружен источник: Instagram")
        raw_text = get_instagram_content(url_source)
    else:
        print("[PIPELINE] Обнаружен источник: Web-страница")
        raw_text = scrape_web_article(url_source)
        
    if not raw_text:
        print("[PIPELINE-ERROR] Не удалось извлечь контент из указанного источника.")
        return False
        
    print(f"[PIPELINE] Контент успешно извлечен ({len(raw_text)} символов).")
    
    # 2. Check for Gemini API Key
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    
    if not api_key:
        # Buffer Mode: Save raw text for the AI agent to process
        buffer_data = {
            "source": url_source,
            "is_youtube": is_youtube,
            "is_instagram": is_instagram,
            "raw_text": raw_text
        }
        buffer_path = os.path.join("scratch", "pending_extraction.json")
        os.makedirs("scratch", exist_ok=True)
        
        with open(buffer_path, "w", encoding="utf-8") as f:
            json.dump(buffer_data, f, ensure_ascii=False, indent=2)
            
        print("\n=======================================================")
        print("[PIPELINE] ВНИМАНИЕ: GEMINI_API_KEY не обнаружен в .env!")
        print("Сырой текст успешно сохранен в буфер:")
        print(f"-> {buffer_path}")
        print("-------------------------------------------------------")
        print("Чтобы завершить обработку, просто попросите меня в чате:")
        print("'Обработай буфер обучения' - и я мгновенно сгенерирую")
        print("статью в /knowledge_base/ и навыки в /_core/agents/skills/!")
        print("=======================================================")
        return True
        
    # 3. API Mode: Call Gemini directly via zero-dependency HTTP POST
    print("[PIPELINE] Вызов API Gemini для структурирования контента...")
    
    prompt = f"""You are a Lead Data Architect & Educator.
Analyze the following raw article/transcript content:
---
{raw_text}
---

Your task is to break this down into two distinct streams:
1. Stream A (Conceptual Markdown): A deep, highly structured, beautiful conceptual markdown article for human learning. Write in Russian. Include Outfit/JetBrains fonts hints, elegant headers, and clear summaries.
2. Stream B (Executable Agent Skill): A structured JSON skill payload containing directives, context requirements, code snippets, and evaluation criteria that a coding subagent can easily load to learn this specific expertise.

You MUST respond strictly with a single, valid JSON object containing exactly these keys:
{{
  "slug": "url-friendly-slug-for-filenames-lowercase",
  "title": "Clean Russian Title of the Topic",
  "knowledge_base_md": "Markdown content for Stream A in Russian...",
  "agent_skill": {{
    "skill_name": "lowercase_slug",
    "version": "1.0.0",
    "description": "Russian description...",
    "category": "backend | frontend | qa | design | marketing",
    "context_requirements": ["list", "of", "libs"],
    "agent_directives": ["instruction 1 in Russian", "instruction 2 in Russian"],
    "code_snippets": [
      {{
        "title": "Snippet Title in Russian",
        "language": "python | javascript | css",
        "code": "code content"
      }}
    ],
    "evaluation_criteria": ["criteria 1 in Russian", "criteria 2 in Russian"]
  }}
}}
"""

    gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + api_key
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(gemini_url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            
        raw_response_text = res['candidates'][0]['content']['parts'][0]['text']
        structured_data = json.loads(raw_response_text)
        
        # 4. Save Stream A (.md) & Stream B (.skills)
        slug = structured_data.get("slug", "extracted_topic").lower()
        title = structured_data.get("title", "Новые знания")
        kb_md = structured_data.get("knowledge_base_md", "")
        skill_payload = structured_data.get("agent_skill", {})
        
        # Stream A: Knowledge Base (Obsidian vault integration)
        obsidian_vault = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
        if obsidian_vault:
            # Normalize path for Windows compatibility
            obsidian_vault = os.path.normpath(obsidian_vault)
            kb_dir = os.path.join(obsidian_vault, "knowledge_base")
            print(f"[PIPELINE] Обнаружено хранилище Obsidian. Статьи сохраняются по пути: {kb_dir}")
        else:
            kb_dir = "knowledge_base"
            
        os.makedirs(kb_dir, exist_ok=True)
        kb_file_path = os.path.join(kb_dir, f"{slug}.md")
        with open(kb_file_path, "w", encoding="utf-8") as f:
            f.write(kb_md)
        print(f"[PIPELINE-SUCCESS] Поток А сохранен: {kb_file_path}")
        
        # Stream B: Executable Agent Skills
        skills_dir = os.path.join("_core", "agents", "skills")
        os.makedirs(skills_dir, exist_ok=True)
        skill_file_path = os.path.join(skills_dir, f"{slug}.skills")
        with open(skill_file_path, "w", encoding="utf-8") as f:
            json.dump(skill_payload, f, ensure_ascii=False, indent=2)
        print(f"[PIPELINE-SUCCESS] Поток Б сохранен: {skill_file_path}")
        
        # Log to team log
        log_entry = f"\n- **[{os.popen('date /t').read().strip()}] [Orchestrator] [EDUCATION]** Успешно импортирован новый навык: '{title}' (сохранены {kb_file_path} и {skill_file_path})."
        with open(os.path.join("_core", "logs", "team_log.md"), "a", encoding="utf-8") as f:
            f.write(log_entry)
            
        return True
        
    except Exception as e:
        print(f"[PIPELINE-ERROR] Не удалось вызвать API Gemini или разобрать ответ: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python pipeline.py <URL>")
        sys.exit(1)
        
    source = sys.argv[1]
    run_extraction_pipeline(source)
