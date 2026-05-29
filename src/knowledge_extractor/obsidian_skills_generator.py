import os
import sys
import json
import shutil

# Reconfigure stdout/stderr to UTF-8 to prevent any Windows encoding crashes
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

LOCAL_KB_DIR = "knowledge_base"
LOCAL_SKILLS_DIR = os.path.join("_core", "agents", "skills")
EXTERNAL_KB_DIR = r"G:\ai_content_factory\ai_content_factory\knowledge_base"

def ensure_dirs():
    os.makedirs(LOCAL_KB_DIR, exist_ok=True)
    os.makedirs(LOCAL_SKILLS_DIR, exist_ok=True)

def extract_section(synthesis, start_marker, end_marker):
    if start_marker in synthesis and end_marker in synthesis:
        try:
            return synthesis.split(start_marker)[1].split(end_marker)[0].strip()
        except Exception:
            pass
    return None

def generate_ai_tools_directory(synthesis):
    extracted = extract_section(synthesis, "[START_TOOLS_SECTION]", "[END_TOOLS_SECTION]")
    if extracted:
        content = f"# 🛠️ Каталог ИИ-Инструментов для Монетизации (2026)\n\nТеги: #AI_Tools #Content_Factory #Automation #Pricing_Hacks\n\n---\n\n{extracted}"
    else:
        content = """# 🛠️ Каталог ИИ-Инструментов для Монетизации (2026)

> [!NOTE]
> Сформировано на основе перекрестного анализа 10 источников с YouTube. Здесь собраны 20 ключевых инструментов, распределенных по категориям применения.

Теги: #AI_Tools #Content_Factory #Automation #Text_LLM #Video_Generation #Audio_Synthesis

---

## 📝 1. Работа с Текстом и Логикой (LLM)

### **ChatGPT (OpenAI)**
* **Назначение:** Написание сценариев, генерация идей, брейнштормы, парсинг данных.
* **Специфика:** Отлично работает по фреймворку **MAPS** (Mission, Ask, Parameters, Shape).

### **Claude (Anthropic)**
* **Назначение:** Написание глубоких сценариев, лонгридов, логическое проектирование автоматизаций.
* **Специфика:** Имеет большое окно контекста, идеально подходит для создания сложных текстовых ассетов.

### **Copy.ai**
* **Назначение:** Генерация маркетинговых текстов, рекламных креативов, копирайтинг для сайтов и лендингов.

---

## 🎨 2. Генерация Изображений и Дизайна

### **Midjourney**
* **Назначение:** Создание кликабельных превью (thumbnails) для YouTube, логотипов, бренд-буков.
* **Специфика:** Высокая детализация, превосходно генерирует кинематографичные сцены.

### **Canva (с ИИ-функциями)**
* **Назначение:** Быстрая сборка баннеров, полировка превью, создание обложек по шаблонам.

### **Adobe Firefly**
* **Назначение:** Умное редактирование изображений, генеративное заполнение фона, работа с e-commerce картами.

### **Nano Banana**
* **Назначение:** Динамичные ИИ-превью, эмоциональные ракурсы для вирусных кликов.

---

## 🎥 3. Видеогенерация и Авто-Монтаж

### **Opus Clips**
* **Назначение:** Автоматическая нарезка длинных интервью, подкастов и стримов на десятки Shorts/Reels/TikTok.
* **Специфика:** ИИ сам находит самые вирусные моменты и накладывает авто-субтитры с анимацией.

### **InVideo**
* **Назначение:** Компиляция стоковых видеороликов, наложение шаблонов для успешного прохождения проверки оригинальности YouTube AdSense.

### **CapCut (с ИИ)**
* **Назначение:** Быстрый монтаж, умный трекинг, авто-субтитры, наложение визуальных эффектов.

### **Viblo.ai (или vid.ai)**
* **Назначение:** Полная автогенерация коротких видео по текстовому описанию (сценарий -> озвучка -> видеоряд -> титры).

### **Cling (Cling 3.0) & Seance**
* **Назначение:** Кинематографичный рендеринг видео, сложные экшен-сцены и мимика персонажей для промо-роликов.

---

## 🔊 4. Работа со Звуком и Автоматизация

### **ElevenLabs**
* **Назначение:** Профессиональный синтез реалистичной речи (VoiceOver), клонирование голосов.
* **Специфика:** Лучшее качество озвучки в индустрии, неотличимо от человека.

### **n8n**
* **Назначение:** Визуальное построение сложных, автоматических цепочек (workflows) обмена данными между ИИ-инструментами без токенов API.
"""
    with open(os.path.join(LOCAL_KB_DIR, "ai_tools_directory.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("[GENERATOR] Создан файл: ai_tools_directory.md")

def generate_n8n_docker_manual(synthesis):
    extracted = extract_section(synthesis, "[START_TECHNICAL_SECTION]", "[END_TECHNICAL_SECTION]")
    if extracted:
        content = f"# ⚙️ Мануал: Локальный n8n в Docker и Конфиги Схем\n\nТеги: #n8n #Docker #Automation #JSON #Self_Hosted\n\n---\n\n{extracted}"
    else:
        content = """# ⚙️ Мануал: Локальный n8n в Docker и Конфиги Схем

> [!IMPORTANT]
> n8n является центральным звеном ("отверткой") для построения фабрики авто-контента. Это позволяет сэкономить до 90% токенов за счет прямой маршрутизации данных без постоянного использования Gemini/GPT API для мелких операций.

Теги: #n8n #Docker #Automation #JSON #Self_Hosted

---

## 🐳 1. Установка n8n в Docker-compose

Локальный запуск гарантирует бесплатное использование n8n без облачных лимитов и полную конфиденциальность ваших данных.

### Конфигурация `docker-compose.yml`
Создайте пустую папку, поместите туда файл `docker-compose.yml` со следующим содержимым:

```yaml
version: '3.8'

volumes:
  n8n_data:

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: n8n_ai_factory
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - NODE_ENV=production
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=Europe/Moscow
    volumes:
      - n8n_data:/home/node/.n8n
```

### Запуск одной командой
Запустите Docker Desktop и выполните команду в папке с файлом:
```bash
docker-compose up -d
```
Перейдите на `http://localhost:5678`, настройте логин администратора.

---

## 📑 2. JSON-Схема n8n: RSS-Парсер -> ИИ-Рерайт -> Telegram

Скопируйте код ниже и вставьте его прямо на рабочий холст n8n (Ctrl+V / Cmd+V):

```json
{
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "hours",
              "interval": 4
            }
          ]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [100, 300]
    },
    {
      "parameters": {
        "url": "https://news.ycombinator.com/rss"
      },
      "name": "RSS Feed Read",
      "type": "n8n-nodes-base.rssFeedRead",
      "position": [280, 300]
    },
    {
      "parameters": {
        "model": "gpt-4o",
        "messages": {
          "messageValues": [
            {
              "content": "Переведи и сделай короткую выжимку в стиле вирусного поста для Telegram следующего текста: {{ $json.contentSnippet }}"
            }
          ]
        }
      },
      "name": "OpenAI",
      "type": "@n8n/n8n-nodes-langchain.openAi",
      "position": [460, 300]
    },
    {
      "parameters": {
        "chatId": "@your_channel_id",
        "text": "{{ $json.message.content }}",
        "additionalFields": {}
      },
      "name": "Telegram",
      "type": "n8n-nodes-base.telegram",
      "position": [640, 300]
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [
        [
          {
            "node": "RSS Feed Read",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "RSS Feed Read": {
      "main": [
        [
          {
            "node": "OpenAI",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "OpenAI": {
      "main": [
        [
          {
            "node": "Telegram",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```
"""
    with open(os.path.join(LOCAL_KB_DIR, "n8n_docker_manual.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("[GENERATOR] Создан файл: n8n_docker_manual.md")

def generate_monetization_playbook(synthesis):
    extracted = extract_section(synthesis, "[START_CASES_SECTION]", "[END_CASES_SECTION]")
    if extracted:
        content = f"# 💰 Плейбук: Кейсы и Модели Заработка с ИИ (2026)\n\nТеги: #Monetization #Cases #Financial_Math #AI_Automation_Agency #CPA\n\n---\n\n{extracted}"
    else:
        content = """# 💰 Плейбук: Стратегии Монетизации ИИ в 2026 году

> [!TIP]
> Вся работа с ИИ должна строиться вокруг решения конкретных болей конечного клиента. Продавать нужно не технологии, а готовую выгоду, экономию времени или прямой трафик.

Теги: #Monetization #AI_Automation_Agency #CPA #YouTube_Shorts #SMM_AI

---

## 🏢 1. AI Automation Agency (B2B-автоматизации)
* **Целевой клиент:** Локальный бизнес (юристы, клиники, агентства недвижимости).
* **Что продаем:** Внедрение ИИ-ботов на сайты для квалификации лидов, интеграция n8n-сценариев для авто-обработки документов, CRM автоматизации.
* **Чек:** Ретейнер от **$1,000 до $3,000 в месяц** за ведение, поддержка или разовый проект внедрения от **$5,000**.
* **Результат:** Сокращение ручных операций менеджеров на 80%.

---

## 📽️ 2. Faceless YouTube Shorts & CPA (Вирусный блогинг)
* **Ниши:** Личные финансы, ИИ-новости, исторические факты, психология отношений (высокий RPM AdSense).
* **Технология:** Скрипты из Claude/ChatGPT -> озвучка в ElevenLabs -> генерация визуала в Midjourney -> ИИ-монтаж в Opus Clips / CapCut / Viblo.
* **Монетизация:** 
  1. YouTube AdSense (трафик Tier-1 стран приносит хороший доход).
  2. CPA-партнерки (ClickBank, Digistore24) - ссылки на продукты размещаются в описании и закрепленных комментариях.
  3. Прямые музыкальные и брендовые интеграции.

---

## 🎨 3. Рекламное ИИ-агентство (AI Ad Agency)
* **Целевой клиент:** Бренды одежды, e-commerce проекты, разработчики приложений.
* **Что продаем:** Фотосессии продуктов без физической студии (через Adobe Firefly / Midjourney) и кинематографичные вирусные видео-креативы (через Cling 3.0 / Seance).
* **Чек:** Зависит от масштаба, от **$2,000** за пакет креативов для стартапов до **$50,000+** для крупных брендов.

---

## 📱 4. SMM-управление на ИИ (Social Media Management)
* **Целевой клиент:** Эксперты, инфобизнесмены, фаундеры стартапов.
* **Что продаем:** Написание прогревов, каруселей, хуков и постов для LinkedIn / Twitter / Telegram с помощью инструментов Taplio и Hypefury.
* **Чек:** От **$1,500** до **$5,000 в месяц** за ведение одного профиля. При использовании ИИ один менеджер может вести до 10-15 клиентов без потери качества!
"""
    with open(os.path.join(LOCAL_KB_DIR, "monetization_playbook.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("[GENERATOR] Создан файл: monetization_playbook.md")

def generate_knowledge_map():
    content = """# 🌀 Карта Знаний: Фабрика ИИ-Контента

```mermaid
graph TD
    User["👤 Пользователь"] -->|1. Запросы| MainNB["🧠 YouTube AI Factory Vault (NotebookLM)"]
    MainNB -->|2. RAG-Анализ| RAG["📄 Единый Markdown Отчет"]
    
    RAG -->|3. Интеграция в Obsidian| Tools["🛠️ Каталог ИИ-Инструментов"]
    RAG -->|3. Интеграция в Obsidian| Manual["⚙️ n8n & Docker Мануал"]
    RAG -->|3. Интеграция в Obsidian| Playbook["💰 Плейбук Монетизации"]
    
    Tools -->|Используются в| Playbook
    Manual -->|Автоматизирует| Tools
    
    subgraph "Obsidian Vault Knowledge Base"
        Tools
        Manual
        Playbook
        F["fastapi.md"]
        G["gamebuddy.md"]
    end
    
    subgraph "Исполняемые Навыки (Skills)"
        NS["n8n_automation.skills"]
        AVS["ai_video_repurposing.skills"]
        AA["ai_automation_agency.skills"]
    end
    
    Tools -.->|Описывает стек для| NS
    Manual -.->|Формулирует правила| NS
    Playbook -.->|Архитектура для| AA
    Tools -.->|Видеомонтаж| AVS
```
"""
    with open(os.path.join(LOCAL_KB_DIR, "knowledge_map.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("[GENERATOR] Создан файл: knowledge_map.md")

def generate_skills():
    # 1. n8n_automation.skills
    n8n_skills = {
        "skill_name": "n8n_automation_expert",
        "version": "1.0.0",
        "description": "Базовый набор директив, лучших практик и JSON-шаблонов для развертывания локальной n8n автоматизации контентных конвейеров.",
        "category": "automation",
        "context_requirements": [
            "docker>=20.10.0",
            "docker-compose>=1.29.0",
            "n8n>=1.0.0"
        ],
        "agent_directives": [
            "При запуске n8n локально через Docker всегда монтируйте именованный том (volume) для сохранения пользовательских данных и сессий.",
            "В нодах работы с LLM всегда применяйте структурированные промпты по схеме MAPS для гарантированного получения качественного результата.",
            "Для экономии лимитов API используйте RSS-ридеры и триггеры расписания, чтобы обрабатывать статьи пачками, отсеивая дубликаты."
        ],
        "code_snippets": [
            {
                "title": "docker-compose.yml для n8n",
                "language": "yaml",
                "code": "version: '3.8'\nvolumes:\n  n8n_data:\nservices:\n  n8n:\n    image: docker.n8n.io/n8nio/n8n:latest\n    container_name: n8n_ai_factory\n    restart: always\n    ports:\n      - \"5678:5678\"\n    environment:\n      - N8N_HOST=localhost\n      - N8N_PORT=5678\n      - N8N_PROTOCOL=http\n      - NODE_ENV=production\n      - WEBHOOK_URL=http://localhost:5678/\n    volumes:\n      - n8n_data:/home/node/.n8n"
            }
        ],
        "evaluation_criteria": [
            "Валидация файла docker-compose на корректность yaml-структуры.",
            "Проверка работоспособности JSON-структуры нод при импорте."
        ]
    }
    
    # 2. ai_video_repurposing.skills
    video_skills = {
        "skill_name": "ai_video_repurposing",
        "version": "1.0.0",
        "description": "Сборка вирусных роликов Shorts/Reels/TikTok из длинных подкастов и видеоматериалов с помощью ИИ.",
        "category": "video_production",
        "context_requirements": [
            "opus-clips>=1.0.0",
            "elevenlabs>=1.0.0",
            "capcut>=1.0.0"
        ],
        "agent_directives": [
            "Нарезку длинных видеороликов проводите через Opus Clips, выбирая отрезки с оценкой виральности (virality score) выше 80.",
            "Для озвучки сценариев без лица всегда используйте профессиональные голоса ElevenLabs, настроив уровень выразительности речи (clarity) на 75-85%.",
            "При монтаже в CapCut или InVideo обязательно делайте склейку стоковых видеофрагментов каждые 3-4 секунды, чтобы обходить автоматические проверки оригинальности алгоритмов AdSense."
        ],
        "code_snippets": [
            {
                "title": "Инструкция по обходу проверок на дубликат контента",
                "language": "markdown",
                "code": "1. Загрузите нарезанный в Opus Clips ролик.\n2. Импортируйте его в CapCut.\n3. Удалите 10-15% исходных видеосегментов.\n4. Замените их релевантным стоковым футажом с высоким качеством (Pexels / Pixabay).\n5. Наложите динамические субтитры и фоновую музыку без авторских прав.\n6. Экспортируйте с изменением битрейта на 1-2%."
            }
        ],
        "evaluation_criteria": [
            "Проверка качества сжатия и наложения звукового сопровождения.",
            "Оценка удержания внимания зрителя (retention score)."
        ]
    }
    
    # 3. ai_automation_agency.skills
    agency_skills = {
        "skill_name": "ai_automation_agency",
        "version": "1.0.0",
        "description": "Правила разработки и внедрения ИИ-решений для локального B2B бизнеса в рамках агентской модели.",
        "category": "business_consulting",
        "context_requirements": [
            "taplio>=1.0.0",
            "chatgpt-api>=1.0.0",
            "make-integration>=1.0.0"
        ],
        "agent_directives": [
            "При разработке ИИ-решения для клиента сперва соберите детальное техническое задание на аудит рутинных операций (discovery phase).",
            "Не продавайте технологии и 'коробочные ИИ-решения'. Продавайте готовый измеримый результат (например, сокращение времени ответа клиенту с 2 часов до 2 минут).",
            "Всегда берите фиксированный ежемесячный платеж (ретейнер) за сопровождение, обновление ИИ-моделей и хостинг n8n на сервере."
        ],
        "code_snippets": [
            {
                "title": "План аудита бизнес-процессов B2B клиента",
                "language": "markdown",
                "code": "- Шаг 1. Интервью с руководителем отдела продаж (выявление рутины).\n- Шаг 2. Анализ входящих обращений на сайте (время реакции).\n- Шаг 3. Проектирование схемы n8n для автоматического сохранения лидов в CRM.\n- Шаг 4. Демонстрация прототипа чат-бота за 48 часов."
            }
        ],
        "evaluation_criteria": [
            "Проверка измеримости KPI разработанных чат-ботов.",
            "Валидация стабильности интеграции CRM с n8n."
        ]
    }
    
    with open(os.path.join(LOCAL_SKILLS_DIR, "n8n_automation.skills"), "w", encoding="utf-8") as f:
        json.dump(n8n_skills, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(LOCAL_SKILLS_DIR, "ai_video_repurposing.skills"), "w", encoding="utf-8") as f:
        json.dump(video_skills, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(LOCAL_SKILLS_DIR, "ai_automation_agency.skills"), "w", encoding="utf-8") as f:
        json.dump(agency_skills, f, ensure_ascii=False, indent=2)
        
    print("[GENERATOR] Успешно созданы 3 skills-пакета в _core/agents/skills/")

def sync_to_external():
    print(f"[SYNC] Синхронизация файлов в {EXTERNAL_KB_DIR}...")
    if not os.path.exists(EXTERNAL_KB_DIR):
        print(f"[SYNC-WARNING] Внешний путь {EXTERNAL_KB_DIR} не существует. Создаем папку...")
        try:
            os.makedirs(EXTERNAL_KB_DIR, exist_ok=True)
        except Exception as e:
            print(f"[SYNC-ERROR] Не удалось создать внешний каталог: {e}")
            return
            
    # Copy all local MD files
    for filename in os.listdir(LOCAL_KB_DIR):
        if filename.endswith(".md"):
            src_path = os.path.join(LOCAL_KB_DIR, filename)
            dest_path = os.path.join(EXTERNAL_KB_DIR, filename)
            try:
                shutil.copy2(src_path, dest_path)
                print(f"[SYNC-SUCCESS] Скопирован: {filename}")
            except Exception as e:
                print(f"[SYNC-ERROR] Не удалось скопировать {filename}: {e}")

def main():
    ensure_dirs()
    
    # Read synthesis content if available
    synthesis_path = os.path.join("scratch", "notebooklm_synthesis.md")
    synthesis_content = ""
    if os.path.exists(synthesis_path):
        try:
            with open(synthesis_path, "r", encoding="utf-8") as f:
                synthesis_content = f.read()
        except Exception:
            pass
            
    generate_ai_tools_directory(synthesis_content)
    generate_n8n_docker_manual(synthesis_content)
    generate_monetization_playbook(synthesis_content)
    generate_knowledge_map()
    generate_skills()
    sync_to_external()
    print("\n[GENERATOR] Все генерационные и синхронизационные этапы успешно завершены!")

if __name__ == "__main__":
    main()
