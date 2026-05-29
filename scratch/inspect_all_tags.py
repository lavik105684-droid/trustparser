import os
import json

def inspect_all_tags():
    print("Searching for keywords across all parsed JSON tags...")
    keywords = ["biography", "edge_owner_to_timeline_media", "shortcode", "full_name", "display_url"]
    
    for filename in sorted(os.listdir("scratch")):
        if filename.startswith("logged_in_tag_") and filename.endswith(".json"):
            filepath = os.path.join("scratch", filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                found_keys = [k for k in keywords if k in content]
                if found_keys:
                    print(f"\nMatch in {filename} (size {os.path.getsize(filepath)} bytes): {found_keys}")
                    data = json.loads(content)
                    
                    # Search paths to each found keyword
                    for kw in found_keys:
                        paths = []
                        def find_key(obj, target, current_path=""):
                            if isinstance(obj, dict):
                                for k, v in obj.items():
                                    path = f"{current_path}.{k}" if current_path else k
                                    if k == target:
                                        paths.append((path, v))
                                    find_key(v, target, path)
                            elif isinstance(obj, list):
                                for idx, item in enumerate(obj):
                                    find_key(item, target, f"{current_path}[{idx}]")
                        find_key(data, kw)
                        print(f"  Keyword '{kw}': found {len(paths)} times.")
                        for p, val in paths[:3]:
                            print(f"    Path: {p}")
                            print(f"    Val: {str(val)[:200]}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    inspect_all_tags()
