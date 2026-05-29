import re

def search_text_in_html():
    with open("scratch/messi_post.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    print("Searching for Messi/World Cup keywords in raw HTML...")
    
    # Let's search for "campeones", "messi", "copa", "world cup" case-insensitive
    keywords = ["campeones", "messi", "world cup", "leomessi"]
    for kw in keywords:
        matches = [m.start() for m in re.finditer(re.escape(kw), html, re.IGNORECASE)]
        print(f"Keyword '{kw}': found {len(matches)} occurrences.")
        for idx, pos in enumerate(matches[:5]):
            snippet = html[max(0, pos-60):min(len(html), pos+140)]
            print(f"  Ocr {idx+1}: {repr(snippet)}")

if __name__ == "__main__":
    search_text_in_html()
