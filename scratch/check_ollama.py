import urllib.request
import json

def check_ollama():
    url = "http://localhost:11434/api/tags"
    try:
        req = urllib.request.urlopen(url, timeout=3)
        res = json.loads(req.read().decode("utf-8"))
        print("OLLAMA_CONNECTED")
        print("Available models:")
        for m in res.get("models", []):
            print(f"- {m.get('name')} ({m.get('details', {}).get('parameter_size')})")
        return True
    except Exception as e:
        print(f"OLLAMA_DISCONNECTED: {e}")
        return False

if __name__ == "__main__":
    check_ollama()
