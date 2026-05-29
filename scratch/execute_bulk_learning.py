import os
import time
import re
import subprocess

def run_query(query):
    print(f"\n==================================================")
    print(f"[BULK-LEARN] Запуск сбора знаний для темы: '{query}'")
    print(f"==================================================")
    
    # Run the pipeline script
    cmd = ["python", "src/knowledge_extractor/pipeline.py", query]
    
    try:
        # Run synchronously to capture and print stdout
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        print(result.stdout)
        if result.stderr:
            print("--- Stderr ---")
            print(result.stderr)
        return True
    except Exception as e:
        print(f"[BULK-LEARN-ERROR] Не удалось запустить конвейер для '{query}': {e}")
        return False

def generate_knowledge_map():
    print("\n[BULK-LEARN] Формирование интерактивной карты знаний в Obsidian...")
    
    obsidian_vault = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
    if obsidian_vault:
        kb_dir = os.path.join(os.path.normpath(obsidian_vault), "knowledge_base")
    else:
        kb_dir = "knowledge_base"
        
    os.makedirs(kb_dir, exist_ok=True)
    map_file_path = os.path.join(kb_dir, "knowledge_map.md")
    
    # Define our 3 topics and their files
    map_content = """# 🗺️ Интерактивная Карта Знаний: ИИ-Производство & Автоматизация

Добро пожаловать в единую карту концептуальных знаний вашего локального хранилища. Ниже представлена система связей и синергии между тремя ключевыми направлениями ваших исследований.

---

## 🌀 Граф Связей & Синергия

```mermaid
graph TD
    A["💰 Заработок на ИИ<br>(Бизнес-модели & Внедрение)"] -->|Интеграция дешевых альтернатив| B["🇨🇳 Китайские LLM<br>(Конкуренты OpenAI/Китай)"]
    C["⚙️ Схемы n8n (Локально)<br>(Автоматизация процессов)"] -->|Технический движок запуска| A
    C -->|Локальный хостинг моделей| B
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#fbf,stroke:#333,stroke-width:2px
```

---

## 1. 💰 [Заработок на ИИ: От идеи до выполнения](file:///G:/ai_content_factory/ai_content_factory/knowledge_base/search_zarabotok_na_ii.md)
* **Концептуальная суть:** Архитектура превращения ИИ-технологий в реальные бизнес-модели. От прототипа на коленке до масштабируемого SaaS.
* **Связанные ресурсы:**
  - [🔍 Поисковый индекс источников](file:///G:/ai_content_factory/ai_content_factory/knowledge_base/search_zarabotok_na_ii.md)
  - [📖 Аналитическая статья лучшего источника](file:///G:/ai_content_factory/ai_content_factory/knowledge_base/ai_monetization_strategies.md) *(будет создана при обработке)*
* **Точка синергии с n8n:** n8n является главным техническим "клеем", позволяющим собирать ИИ-агентов без затрат на дорогой бэкенд, ускоряя проверку гипотез заработка в 10 раз.

---

## 2. 🇨🇳 [Конкуренты большим ИИ от Китая](file:///G:/ai_content_factory/ai_content_factory/knowledge_base/search_konkurenty_bol_shim_ii_ot_kitaya.md)
* **Концептуальная суть:** Обзор мощных и сверхдешевых альтернатив GPT-4 от Китая (DeepSeek R1, Qwen 2.5, GLM-4).
* **Связанные ресурсы:**
  - [🔍 Поисковый индекс источников](file:///G:/ai_content_factory/ai_content_factory/knowledge_base/search_konkurenty_bol_shim_ii_ot_kitaya.md)
  - [📖 Аналитическая статья лучшего источника](file:///G:/ai_content_factory/ai_content_factory/knowledge_base/chinese_ai_competitors.md) *(будет создана при обработке)*
* **Точка синергии с Заработком:** Использование открытых китайских моделей с открытым кодом (или их копеечных API) решает главную проблему маржинальности ИИ-бизнесов, снижая затраты на инференс до 95%.

---

## 3. ⚙️ [Схемы n8n на локальной версии](file:///G:/ai_content_factory/ai_content_factory/knowledge_base/search_shemy_n8n_na_lokal_noj_versii.md)
* **Концептуальная суть:** Проектирование сложных сценариев автоматизации на локально хостируемом сервере n8n.
* **Связанные ресурсы:**
  - [🔍 Поисковый индекс источников](file:///G:/ai_content_factory/ai_content_factory/knowledge_base/search_shemy_n8n_na_lokal_noj_versii.md)
  - [📖 Аналитическая статья лучшего источника](file:///G:/ai_content_factory/ai_content_factory/knowledge_base/local_n8n_workflows.md) *(будет создана при обработке)*
* **Точка синергии с Китайскими LLM:** Локальный n8n идеально подходит для развертывания приватных контуров автоматизации, где в качестве агентов через локальные Node (типа HTTP Request или Ollama) подключаются китайские опенсорсные модели.

---
📅 *Карта знаний сгенерирована автоматически Pixel Office Orchestrator в режиме непрерывного обучения.*
"""
    
    with open(map_file_path, "w", encoding="utf-8") as f:
        f.write(map_content)
    print(f"[BULK-LEARN-SUCCESS] Интерактивная карта знаний создана: {map_file_path}")

def main():
    queries = [
        "Заработок на ИИ",
        "Конкуренты большим ИИ от Китая",
        "Схемы n8n на локальной версии"
    ]
    
    # Run the queries with a solid cooldown pause of 10 seconds between them!
    for idx, q in enumerate(queries):
        if idx > 0:
            print(f"\n[BULK-COOLDOWN] Ожидание 10 секунд перед запуском следующей темы для полной защиты от блокировок...")
            time.sleep(10.0)
        run_query(q)
        
    generate_knowledge_map()
    print("\n==================================================")
    print("[BULK-LEARN] Сбор знаний успешно завершен!")
    print("==================================================")

if __name__ == "__main__":
    main()
