import urllib.request
import urllib.error
import ssl

def test_url(url):
    print(f"\nTesting connection to: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    req = urllib.request.Request(url, headers=headers)
    
    # Ignore SSL verification for diagnostic purposes
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            print(f"[SUCCESS] Status code: {response.status}")
            html = response.read().decode("utf-8", errors="ignore")
            print(f"Content length: {len(html)} characters")
            print(f"Snippet: {html[:200]}...")
            return True
    except urllib.error.HTTPError as e:
        print(f"[HTTP-ERROR] Code: {e.code}, Reason: {e.reason}")
    except urllib.error.URLError as e:
        print(f"[URL-ERROR] Reason: {e.reason}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    return False

if __name__ == "__main__":
    test_url("https://www.picuki.com")
    test_url("https://imgsed.com")
    test_url("https://html.duckduckgo.com/html/?q=fastapi")
