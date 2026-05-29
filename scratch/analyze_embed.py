import subprocess
import re

def analyze_embed():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    url = "https://www.instagram.com/nasa/embed/"
    
    cmd = [
        "curl.exe", "-s",
        "-A", ua,
        url
    ]
    
    print("Fetching embed page...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    html = result.stdout
    
    print(f"Embed HTML length: {len(html)}")
    if not html:
        print("Empty HTML.")
        return
        
    with open("scratch/embed_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved to scratch/embed_page.html")
    
    # Search for captions, post text, shortcodes, or class names
    print("\nSearching for class names or elements...")
    # Instagram embed usually contains the username, avatar, and maybe some post items if it's a profile embed?
    # Wait! /nasa/embed/ is the embed for the profile or for a post?
    # Actually, /nasa/embed/ might not be a valid profile embed, but /p/<shortcode>/embed/ is a post embed!
    # Let's check if /nasa/embed/ is a valid endpoint. It returned 200 OK!
    # Let's see what is inside the HTML. Let's search for "nasa" (case-insensitive).
    matches = [m.start() for m in re.finditer(r'nasa', html, re.IGNORECASE)]
    print(f"Found {len(matches)} occurrences of 'nasa'.")
    for idx, pos in enumerate(matches[:5]):
        snippet = html[max(0, pos-50):min(len(html), pos+150)]
        print(f"Occurrence {idx+1}:")
        print(repr(snippet))

if __name__ == "__main__":
    analyze_embed()
