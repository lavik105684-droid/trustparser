import os
import json

def search_nasa():
    print("Searching for 'nasa' in scratch JSON files...")
    for filename in sorted(os.listdir("scratch")):
        if filename.endswith(".json") and filename.startswith("json_tag_"):
            filepath = os.path.join("scratch", filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if "nasa" in content.lower():
                    print(f"File {filename} (size {os.path.getsize(filepath)} bytes) contains 'nasa'!")
                    # Load and print keys/snippets
                    data = json.loads(content)
                    if isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())}")
                        # Print preview
                        print(f"  Preview: {str(data)[:300]}...")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    search_nasa()
