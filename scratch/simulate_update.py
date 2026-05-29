import urllib.request
import json
import time

url = "http://localhost:8000/api/task"
data = {
    "agent": "QA Engineer",
    "task": "Все тесты успешно пройдены! Интеграционные WebSocket-тесты завершены.",
    "status": "IDLE"
}

headers = {"Content-Type": "application/json"}
req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")

try:
    print("Sending API update request to set QA Engineer to IDLE...")
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode("utf-8"))
        print("API Response:", res)
        
    print("Wait 3 seconds for UI inspection...")
    time.sleep(3)
    
    # Restore QA Engineer back to ACTIVE status
    data["task"] = "Аудит скриптов парсинга и валидация структуры кодовой базы."
    data["status"] = "ACTIVE"
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    print("Sending API update request to restore QA Engineer to ACTIVE...")
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode("utf-8"))
        print("API Response:", res)
        
except Exception as e:
    print("Error updating agent state:", e)
