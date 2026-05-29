import os
import time
import json
import sys

# Add src/knowledge_extractor to path to import instagram_extractor
sys.path.append(os.path.join(os.getcwd(), "src", "knowledge_extractor"))
from instagram_extractor import get_instagram_content

def scrape_examples():
    urls = [
        "https://www.instagram.com/p/DY4UKWaACBo/",
        "https://www.instagram.com/reel/DY6EvpayD92/",
        "https://www.instagram.com/reel/DY4XIKKMuy6/",
        "https://www.instagram.com/reel/DY157l3z-Qx/",
        "https://www.instagram.com/reel/DYPr4D4xW8p/",
        "https://www.instagram.com/reel/DYN-9sust5P/",
        "https://www.instagram.com/reel/DX648KnDDjm/"
    ]
    
    results = {}
    print(f"[EXAMPLES] Запуск извлечения данных из {len(urls)} примеров пользователя...")
    
    for idx, url in enumerate(urls):
        if idx > 0:
            print("[EXAMPLES-COOLDOWN] Ожидание 6 секунд перед следующим запросом...")
            time.sleep(6.0)
            
        print(f"\n[EXAMPLES] Скрапинг ({idx+1}/{len(urls)}): {url}")
        content = get_instagram_content(url)
        if content:
            results[url] = content
            print(f"[EXAMPLES-SUCCESS] Успешно извлечено {len(content)} символов.")
        else:
            print(f"[EXAMPLES-FAIL] Не удалось получить контент для: {url}")
            
    # Save raw results for analysis
    os.makedirs("scratch", exist_ok=True)
    with open("scratch/scraped_examples_raw.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[EXAMPLES-COMPLETE] Успешно сохранено {len(results)} результатов в scratch/scraped_examples_raw.json")

if __name__ == "__main__":
    scrape_examples()
