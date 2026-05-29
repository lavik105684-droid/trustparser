import urllib.request
import json

url = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=h9X-q8--0wg&format=json"

try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode("utf-8"))
        print("OEMBED_TITLE:", data.get("title"))
        print("OEMBED_AUTHOR:", data.get("author_name"))
        print("OEMBED_DATA:", json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print("Error querying oEmbed:", e)
