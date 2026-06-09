import requests
import json
import re

# 1. ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (Конфигурация)
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

def clean_and_parse_json(raw_text):
    """
    Очищает ответ от Gemini от markdown-оберток и мусорного текста,
    возвращая распарсенный JSON.
    """
    # Удаляем markdown-теги
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()

    # Обрезаем все до первой { и после последней }
    start_idx = cleaned.find('{')
    end_idx = cleaned.rfind('}')

    if start_idx == -1 or end_idx == -1:
        raise ValueError("В ответе не найдены JSON скобки {}")

    json_str = cleaned[start_idx:end_idx+1]

    try:
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка парсинга JSON: {e}\nТекст: {json_str}")

def main():
    try:
        print("Начинаем генерацию контента AntiAI...")

        # ШАГ 1: ГЕНЕРАЦИЯ ТЕКСТА И СМЫСЛОВ (Google Gemini API)
        print("Шаг 1. Запрос к Gemini...")
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

        prompt = (
            'Напиши сочный, циничный пост-разоблачение ИИ для блога AntiAI. '
            'Тема должна быть выбрана случайно. Выдай строго чистую строку JSON '
            'с тремя полями (без лишнего текста, без markdown-оберток): '
            '{"title": "Краткий заголовок для обложки на английском", '
            '"pain": "Описание бага или проблемы для генерации картинки во Flux на английском", '
            '"caption": "Финальный текст поста для Инстаграм на русском с абзацами и хэштегами"}. '
            'Пиши в стиле жесткого технического аналитика.'
        )

        gemini_payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        gemini_headers = {"Content-Type": "application/json"}
        gemini_resp = requests.post(gemini_url, json=gemini_payload, headers=gemini_headers)
        gemini_resp.raise_for_status()

        gemini_data = gemini_resp.json()
        try:
            raw_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise ValueError(f"Неожиданный формат ответа Gemini: {gemini_data}")

        print("Ответ от Gemini получен.")

        # ШАГ 2: ВАЛИДАЦИЯ И ОЧИСТКА JSON
        print("Шаг 2. Парсинг и очистка JSON...")
        content = clean_and_parse_json(raw_text)

        title = content.get("title")
        pain = content.get("pain")
        caption = content.get("caption")

        if not title or not pain or not caption:
            raise ValueError("Отсутствуют обязательные поля в JSON-ответе Gemini.")

        print("JSON успешно разобран.")

        # ШАГ 3: ГЕНЕРАЦИЯ ГРАФИКИ (OpenRouter API)
        print("Шаг 3. Генерация графики через OpenRouter (Flux)...")
        openrouter_url = "https://openrouter.ai/api/v1/images/generations"
        openrouter_headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Запрос 1: Обложка карусели
        print("   - Генерация обложки...")
        cover_prompt = f"{title} from Gemini, 3D isometric model, stylized miniature toy aesthetic, clean defined edges, completely shadowless rendering, ultra bright perfectly even ambient lighting from all angles, pure white background with zero shadows, 4K resolution"

        cover_payload = {
            "model": "black-forest-labs/flux-1-schnell",
            "prompt": cover_prompt
        }

        cover_resp = requests.post(openrouter_url, json=cover_payload, headers=openrouter_headers)
        cover_resp.raise_for_status()
        cover_url = cover_resp.json()["data"][0]["url"]

        # Запрос 2: Слайд боли
        print("   - Генерация слайда боли...")
        pain_prompt = f"{pain} from Gemini, funny error vector illustration, modern tech style, high key lighting, maximum brightness, shadow removal, pure white background with zero shadows"

        pain_payload = {
            "model": "black-forest-labs/flux-1-schnell",
            "prompt": pain_prompt
        }

        pain_resp = requests.post(openrouter_url, json=pain_payload, headers=openrouter_headers)
        pain_resp.raise_for_status()
        pain_url = pain_resp.json()["data"][0]["url"]

        print("Изображения сгенерированы.")

        # ШАГ 4: ФИНАЛЬНАЯ ОТПРАВКА (Telegram Bot API)
        print("Шаг 4. Отправка в Telegram...")
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        message_text = f"{caption}\n\n"
        message_text += f"🖼 Обложка: {cover_url}\n"
        message_text += f"🖼 Слайд боли: {pain_url}"

        telegram_payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message_text,
            "parse_mode": "HTML"
        }

        tg_resp = requests.post(telegram_url, json=telegram_payload)
        tg_resp.raise_for_status()

        print("Пост успешно отправлен в Telegram!")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети/API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Ответ сервера: {e.response.text}")
    except ValueError as e:
        print(f"Ошибка данных: {e}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")

if __name__ == "__main__":
    main()
