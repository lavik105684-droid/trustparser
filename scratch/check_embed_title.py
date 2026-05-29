import re

def check_title():
    with open("scratch/messi_embed.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    title = title_match.group(1) if title_match else "No title found"
    print(f"Title tag content: {title}")
    
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE)
    h1 = h1_match.group(1) if h1_match else "No H1 found"
    print(f"H1 tag content: {h1}")
    
    # Search for "login" or similar keywords
    login_count = len(re.findall(r'login', html, re.IGNORECASE))
    print(f"Occurrences of 'login': {login_count}")

if __name__ == "__main__":
    check_title()
