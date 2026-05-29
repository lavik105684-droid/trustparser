import json
import os
import subprocess

def test_url(url, headers_dict, desc, log_file):
    log_file.write(f"\n--- Testing: {desc} ---\n")
    log_file.write(f"URL: {url}\n")
    
    cmd = ["curl.exe", "-s", "-i"]
    for k, v in headers_dict.items():
        cmd.extend(["-H", f"{k}: {v}"])
    cmd.append(url)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        raw_res = result.stdout
        
        # Parse headers and body
        parts = raw_res.split("\r\n\r\n", 1)
        headers = parts[0]
        body = parts[1] if len(parts) > 1 else ""
        
        first_line = headers.split("\r\n")[0]
        log_file.write(f"Status line: {first_line}\n")
        log_file.write(f"Headers size: {len(headers)}\n")
        log_file.write(f"Response body length: {len(body)}\n")
        
        # Check if 429
        if "429" in first_line:
            log_file.write("Status: 429 Too Many Requests\n")
        elif "200" in first_line:
            log_file.write("Status: 200 OK\n")
            log_file.write("Body preview (first 500 chars):\n")
            log_file.write(body[:500] + "\n")
        else:
            log_file.write(f"Status: Other ({first_line})\n")
            
        return "200" in first_line
    except Exception as e:
        log_file.write(f"Exception: {e}\n")
        return False

def run_tests():
    # Load env
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

    session_id = os.environ.get("INSTAGRAM_SESSION_ID", "").strip()
    user_id = os.environ.get("INSTAGRAM_USER_ID", "").strip()
    csrf_token = os.environ.get("INSTAGRAM_CSRF_TOKEN", "").strip()
    cookie_str = f"sessionid={session_id}; ds_user_id={user_id}; csrftoken={csrf_token}"
    
    # Common Chrome UA
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    
    with open("scratch/instagram_test_results.txt", "w", encoding="utf-8") as f:
        # Test 1: API profile info WITH all credentials
        h1 = {
            "User-Agent": ua,
            "X-IG-App-ID": "936619743392459",
            "X-CSRFToken": csrf_token,
            "Cookie": cookie_str,
            "Referer": "https://www.instagram.com/"
        }
        test_url("https://www.instagram.com/api/v1/users/web_profile_info/?username=nasa", h1, "API Web Profile Info WITH credentials", f)
        
        # Test 2: API profile info WITHOUT credentials
        h2 = {
            "User-Agent": ua,
            "X-IG-App-ID": "936619743392459",
            "Referer": "https://www.instagram.com/"
        }
        test_url("https://www.instagram.com/api/v1/users/web_profile_info/?username=nasa", h2, "API Web Profile Info WITHOUT credentials", f)
        
        # Test 3: Embed page for a username (very useful for public scraping!)
        h3 = {
            "User-Agent": ua
        }
        test_url("https://www.instagram.com/nasa/embed/", h3, "Embed page (public)", f)

        # Test 4: Main profile page without cookies
        h4 = {
            "User-Agent": ua
        }
        test_url("https://www.instagram.com/nasa/", h4, "Main profile page WITHOUT cookies", f)

    print("Done! Results written to scratch/instagram_test_results.txt")

if __name__ == "__main__":
    run_tests()
