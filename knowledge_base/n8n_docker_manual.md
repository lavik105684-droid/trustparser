# ⚙️ Мануал: Локальный n8n в Docker и Конфиги Схем

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
