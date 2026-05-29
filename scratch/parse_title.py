import re

html_path = r"C:\Users\lavik\.gemini\antigravity\brain\4b2333aa-7ee4-4292-bb8d-d76aaab77e33\.system_generated\steps\1143\content.md"

try:
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Search for common meta tags in YouTube watch pages
    title_matches = [
        re.search(r'<meta property="og:title" content="(.*?)"', content),
        re.search(r'<meta name="title" content="(.*?)"', content),
        re.search(r'"title":"(.*?)"', content),
        re.search(r'<title>(.*?)</title>', content)
    ]
    
    # Search for descriptions
    desc_matches = [
        re.search(r'<meta property="og:description" content="(.*?)"', content),
        re.search(r'<meta name="description" content="(.*?)"', content),
        re.search(r'"shortDescription":"(.*?)"', content)
    ]
    
    title = "Unknown Video"
    for match in title_matches:
        if match:
            title = match.group(1)
            break
            
    desc = "No Description"
    for match in desc_matches:
        if match:
            desc = match.group(1)
            break
            
    print("EXTRACTED_TITLE:", title)
    print("EXTRACTED_DESC:", desc[:300] + "...")
except Exception as e:
    print("Error parsing HTML:", e)
