import os
import sys
import json
import urllib.request
import urllib.error

# Custom minimal .env parser to maintain zero dependency footprint
def load_env(env_path=".env"):
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def send_telegram_test():
    # Load env variables from root directory
    load_env()
    
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    
    # Check for empty or placeholder values
    if not bot_token or "YOUR_BOT_TOKEN" in bot_token or not chat_id or "YOUR_CHAT_ID" in chat_id:
        print("[ОШИБКА] Учетные данные Telegram не настроены в файле .env!")
        print("Пожалуйста, создайте или откройте файл .env в корневом каталоге проекта и укажите корректные:")
        print("- TELEGRAM_BOT_TOKEN=ваш_токен_бота")
        print("- TELEGRAM_CHAT_ID=имя_вашего_канала (например, @mychannel) или числовой ID")
        sys.exit(1)
        
    print(f"[ИНФО] Отправка тестового запроса в Telegram (Канал/Чат: {chat_id})...")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "⚡ Тест связи Pixel Office с вашим Telegram-каналом успешно ПРОЙДЕН!\n\nВсе системы активны и работают стабильно в реальном времени."
    }
    
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("ok"):
                print("[УСПЕХ] Тестовое сообщение отправлено успешно!")
                print("Ответ Telegram API:", json.dumps(res, ensure_ascii=False, indent=2))
                return True
            else:
                print(f"[ОШИБКА] Telegram API вернул отрицательный ответ: {res}")
                return False
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"[ОШИБКА] Ошибка HTTP от Telegram API: {e.code} {e.reason}")
        print("Детали ошибки:", err_msg)
        return False
    except Exception as e:
        print(f"[ОШИБКА] Не удалось связаться с Telegram API: {e}")
        return False

if __name__ == "__main__":
    send_telegram_test()
