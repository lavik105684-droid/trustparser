import os
import subprocess

def load_env(env_path=".env"):
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def analyze_logged_in_html():
    load_env()
    
    session_id = os.environ.get("INSTAGRAM_SESSION_ID", "").strip()
    user_id = os.environ.get("INSTAGRAM_USER_ID", "").strip()
    csrf_token = os.environ.get("INSTAGRAM_CSRF_TOKEN", "").strip()
    
    if not session_id or not user_id or not csrf_token:
        print("[ERROR] Credentials not found!")
        return
        
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = "https://www.instagram.com/nasa/"
    cookie_str = f"sessionid={session_id}; ds_user_id={user_id}; csrftoken={csrf_token}"
    
    cmd = [
        "curl.exe", "-v",
        "-A", ua,
        "-H", f"Cookie: {cookie_str}",
        "-H", f"X-CSRFToken: {csrf_token}",
        "-H", "Referer: https://www.instagram.com/",
        url
    ]
    
    print("Fetching profile page WITH cookies...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    
    print("--- Stderr (verbose) ---")
    print(result.stderr)
    print("------------------------")
    print(f"Stdout length: {len(result.stdout)}")
    if result.stdout:
        print(result.stdout[:500])

if __name__ == "__main__":
    analyze_logged_in_html()
