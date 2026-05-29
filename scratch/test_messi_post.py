import subprocess

def test_messi_post_verbose():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = "https://www.instagram.com/p/CmYOR5Xq_OC/"
    
    cmd = [
        "curl.exe", "-v",
        "-A", ua,
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Referer: https://www.google.com/",
        url
    ]
    
    print("Fetching Messi's World Cup post (verbose)...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    
    print("--- Stderr (verbose) ---")
    print(result.stderr)
    print("------------------------")
    print(f"Stdout length: {len(result.stdout)}")
    if result.stdout:
        print(result.stdout[:500])

if __name__ == "__main__":
    test_messi_post_verbose()
