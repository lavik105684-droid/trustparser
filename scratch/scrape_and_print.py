import os
import time
import sys

sys.path.append(os.path.join(os.getcwd(), "src", "knowledge_extractor"))
from instagram_extractor import get_instagram_content

def main():
    urls = [
        "https://www.instagram.com/p/DY4UKWaACBo/",
        "https://www.instagram.com/reel/DY6EvpayD92/",
        "https://www.instagram.com/reel/DY4XIKKMuy6/",
        "https://www.instagram.com/reel/DY157l3z-Qx/",
        "https://www.instagram.com/reel/DYPr4D4xW8p/",
        "https://www.instagram.com/reel/DYN-9sust5P/",
        "https://www.instagram.com/reel/DX648KnDDjm/"
    ]
    
    print("START_SCRAPE_OUTPUT")
    for idx, url in enumerate(urls):
        if idx > 0:
            time.sleep(5.0)
        print(f"\n--- URL: {url} ---")
        content = get_instagram_content(url)
        if content:
            print(content)
        else:
            print("FAILED_TO_SCRAPE")
    print("END_SCRAPE_OUTPUT")

if __name__ == "__main__":
    main()
