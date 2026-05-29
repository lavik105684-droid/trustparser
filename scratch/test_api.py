import urllib.request
import urllib.error
import json
import os

def load_env(env_path=".env"):
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env()
api_key = os.environ.get("GEMINI_API_KEY", "").strip()

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
try:
    with urllib.request.urlopen(url) as response:
        res = json.loads(response.read().decode("utf-8"))
        models = res.get("models", [])
        print(f"[УСПЕХ] Успешное подключение! Доступно моделей: {len(models)}")
        for m in models[:10]:
            print(f"- {m.get('name')} ({m.get('displayName')})")
except urllib.error.HTTPError as e:
    print(f"[ОШИБКА] Код: {e.code}, Сообщение: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"[ОШИБКА] {e}")
