import json

def inspect_tag_24():
    filepath = "scratch/logged_in_tag_24.json"
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("Inspecting scratch/logged_in_tag_24.json...")
    
    # We will search recursively for keys like shortcode, display_url, or caption
    results = []
    
    def scan(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                current_path = f"{path}.{k}" if path else k
                if k in ["shortcode", "display_url", "caption", "text", "biography", "username"]:
                    results.append((current_path, k, str(v)[:200]))
                scan(v, current_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                scan(item, f"{path}[{idx}]")
                
    scan(data)
    
    print(f"Found {len(results)} matches:")
    for path, key, val_preview in results[:30]:
        print(f"- Path: {path}")
        print(f"  Key: {key}")
        print(f"  Value: {val_preview}")

if __name__ == "__main__":
    inspect_tag_24()
