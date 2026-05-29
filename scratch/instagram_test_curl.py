import json
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

def test_instagram_connection_curl(target_username="nasa"):
    load_env()
    
    session_id = os.environ.get("INSTAGRAM_SESSION_ID", "").strip()
    user_id = os.environ.get("INSTAGRAM_USER_ID", "").strip()
    csrf_token = os.environ.get("INSTAGRAM_CSRF_TOKEN", "").strip()
    
    if not session_id or not user_id or not csrf_token:
        print("[ERROR] Instagram credentials not found in .env!")
        return False
        
    print(f"[INSTAGRAM-CURL] Testing connection for profile: @{target_username}...")
    
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={target_username}"
    
    cookie_str = f"sessionid={session_id}; ds_user_id={user_id}; csrftoken={csrf_token}"
    
    # Construct curl.exe command
    cmd = [
        "curl.exe", "-v", # verbose mode to see TLS handshake and response headers
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "-H", f"X-IG-App-ID: 936619743392459",
        "-H", f"X-CSRFToken: {csrf_token}",
        "-H", f"Cookie: {cookie_str}",
        "-H", "Referer: https://www.instagram.com/",
        url
    ]
    
    print("Executing command:")
    print(" ".join(cmd))
    
    try:
        # Run curl.exe and get output
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        
        print(f"curl.exe returncode: {result.returncode}")
        print("--- Stderr (verbose logs) ---")
        print(result.stderr)
        print("----------------------------")
        
        raw_output = result.stdout.strip()
        print(f"Raw output length: {len(raw_output)}")
        if not raw_output:
            print("[ERROR] Received empty response from curl.exe")
            return False
            
        # Parse JSON
        try:
            res = json.loads(raw_output)
        except json.JSONDecodeError:
            print("[ERROR] Response is not a valid JSON!")
            print("Server response (first 500 chars):")
            print(raw_output[:500])
            return False
            
        user_info = res.get("data", {}).get("user", {})
        if user_info:
            print("\n[SUCCESS] Successfully connected to Instagram API!")
            print("Account:", user_info.get("username"))
            return True
        else:
            print("[ERROR] API returned empty user data.")
            print("Response:", json.dumps(res, ensure_ascii=False)[:500])
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to run curl request: {e}")
        return False

if __name__ == "__main__":
    test_instagram_connection_curl()
