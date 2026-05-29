import os
import subprocess
import re
import json

def load_env(env_path=".env"):
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def test_dynamic_csrf():
    load_env()
    session_id = os.environ.get("INSTAGRAM_SESSION_ID", "").strip()
    user_id = os.environ.get("INSTAGRAM_USER_ID", "").strip()
    
    if not session_id or not user_id:
        print("[ERROR] sessionid or user_id not found in env!")
        return
        
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    
    # Step 1: Hit main page with sessionid to get a fresh csrftoken
    print("[STEP 1] Fetching main page to get fresh CSRF token...")
    cookie_str = f"sessionid={session_id}; ds_user_id={user_id}"
    
    cmd_init = [
        "curl.exe", "-s", "-i",
        "-A", ua,
        "-H", f"Cookie: {cookie_str}",
        "https://www.instagram.com/"
    ]
    
    res_init = subprocess.run(cmd_init, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    headers_init = res_init.stdout.split("\r\n\r\n")[0]
    
    # Extract csrftoken from Set-Cookie headers
    csrf_token = None
    cookies_found = {}
    
    for line in headers_init.splitlines():
        if line.lower().startswith("set-cookie:"):
            cookie_parts = line.split(":", 1)[1].strip().split(";")
            first_part = cookie_parts[0].strip()
            if "=" in first_part:
                k, v = first_part.split("=", 1)
                cookies_found[k.strip()] = v.strip()
                
    csrf_token = cookies_found.get("csrftoken")
    mid_cookie = cookies_found.get("mid")
    
    print(f"Cookies received in Set-Cookie: {list(cookies_found.keys())}")
    
    if not csrf_token:
        # If not in Set-Cookie, try to parse from the HTML
        print("CSRF token not in headers. Searching HTML...")
        html = res_init.stdout
        # Search for csrf_token in HTML
        csrf_match = re.search(r'"csrf_token"\s*:\s*"([^"]+)"', html)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"Found CSRF token in HTML: {csrf_token}")
        else:
            # Fallback to env csrf token
            csrf_token = os.environ.get("INSTAGRAM_CSRF_TOKEN", "").strip()
            print(f"Fallback to env CSRF token: {csrf_token}")
    else:
        print(f"Successfully obtained fresh CSRF token: {csrf_token}")
        
    if not csrf_token:
        print("[ERROR] Could not obtain CSRF token!")
        return
        
    # Step 2: Hit the profile API using the fresh cookies
    print("\n[STEP 2] Fetching profile API with fresh CSRF token and cookies...")
    
    # Construct complete cookie string
    full_cookies = f"sessionid={session_id}; ds_user_id={user_id}; csrftoken={csrf_token}"
    if mid_cookie:
        full_cookies += f"; mid={mid_cookie}"
        
    url_api = "https://www.instagram.com/api/v1/users/web_profile_info/?username=nasa"
    
    cmd_api = [
        "curl.exe", "-v",
        "-A", ua,
        "-H", f"X-IG-App-ID: 936619743392459",
        "-H", f"X-CSRFToken: {csrf_token}",
        "-H", f"Cookie: {full_cookies}",
        "-H", "Referer: https://www.instagram.com/",
        url_api
    ]
    
    res_api = subprocess.run(cmd_api, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    
    print("--- Stderr (API call) ---")
    print(res_api.stderr)
    print("-------------------------")
    
    raw_out = res_api.stdout.strip()
    print(f"API Output Length: {len(raw_out)}")
    if raw_out:
        print("API Output (first 500 chars):")
        print(raw_out[:500])
        
        # Save output to file
        with open("scratch/api_dynamic_response.json", "w", encoding="utf-8") as f:
            f.write(raw_out)
        print("Saved API response to scratch/api_dynamic_response.json")

if __name__ == "__main__":
    test_dynamic_csrf()
