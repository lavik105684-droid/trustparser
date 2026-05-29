import urllib.request
import urllib.error
import sys
import re
from html.parser import HTMLParser

# Try importing BeautifulSoup as premium parser
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

class CleanTextParser(HTMLParser):
    """
    Zero-dependency HTML to text parser.
    Bypasses structural headers, footers, script, and style blocks.
    """
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.ignore_depth = 0
        self.ignore_tags = {'script', 'style', 'header', 'footer', 'nav', 'noscript', 'iframe', 'head'}

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.ignore_tags:
            self.ignore_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in self.ignore_tags:
            self.ignore_depth = max(0, self.ignore_depth - 1)

    def handle_data(self, data):
        if self.ignore_depth == 0:
            clean_data = data.strip()
            if clean_data:
                # Add spacing after paragraphs or blocks
                self.text_parts.append(clean_data)

    def get_text(self):
        return "\n\n".join(self.text_parts)

def scrape_web_article(url):
    """
    Scrapes and cleans text content from a given web article URL.
    Uses standard urllib.request with a mock browser User-Agent.
    """
    import time
    print(f"[WEB-SCRAPE] Запуск парсинга страницы: {url}")
    print("[WEB-SCRAPE] Пауза 2 секунды для обхода блокировок...")
    time.sleep(2.0)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            charset = response.headers.get_content_charset() or 'utf-8'
            html_content = response.read().decode(charset, errors='replace')
            
        if BeautifulSoup:
            print("[WEB-SCRAPE] Использование BeautifulSoup для извлечения контента...")
            soup = BeautifulSoup(html_content, "html.parser")
            
            # De-clutter DOM
            for element in soup(["script", "style", "header", "footer", "nav", "noscript", "iframe"]):
                element.decompose()
                
            # Try getting main article content block
            main_content = soup.find("article") or soup.find("main") or soup.find("div", {"class": re.compile(r'content|article|post|body')})
            if main_content:
                return main_content.get_text(separator="\n\n").strip()
            else:
                return soup.get_text(separator="\n\n").strip()
        else:
            print("[WEB-SCRAPE] BeautifulSoup не найден. Использование встроенного CleanTextParser...")
            parser = CleanTextParser()
            parser.feed(html_content)
            return parser.get_text().strip()
            
    except urllib.error.URLError as e:
        print(f"[WEB-SCRAPE-ERROR] Ошибка сети/доступности URL: {e}")
        return None
    except Exception as e:
        print(f"[WEB-SCRAPE-ERROR] Непредвиденная ошибка парсинга: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python web_extractor.py <URL>")
        sys.exit(1)
        
    url_target = sys.argv[1]
    content = scrape_web_article(url_target)
    if content:
        print("\n--- Спарсенный контент (первые 500 символов) ---")
        print(content[:500] + "...")
    else:
        print("\n[ФЕЙЛ] Не удалось получить контент страницы.")
