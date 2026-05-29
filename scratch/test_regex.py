import re

def test():
    with open("scratch/html_snippet.txt", "r", encoding="utf-8") as f:
        html = f.read()
        
    print("HTML snippet length:", len(html))
    
    # Try exact match without lazy DOTALL
    pattern = r'"lengthText":\{"accessibility":\{"accessibilityData":\{"label":"[^"]+"\}\},"simpleText":"([^"]+)"\}'
    match = re.search(pattern, html)
    
    if match:
        print("[SUCCESS] Regex matched lengthText:", match.group(1))
    else:
        print("[FAIL] Regex failed to match!")
        # Try finding lengthText raw chunk
        raw_match = re.search(r'"lengthText":\{.*?\}', html)
        if raw_match:
            print("Raw lengthText chunk found:", raw_match.group(0))

if __name__ == "__main__":
    test()
