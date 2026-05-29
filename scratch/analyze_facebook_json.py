import json

def analyze_facebook_json():
    filepath = "scratch/json_tag_13.json"
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("Searching inside json_tag_13.json...")
    
    # We will recursively scan all values for keys or values we need.
    results = []
    
    def scan(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                current_path = f"{path}.{k}" if path else k
                if k in ["biography", "edge_owner_to_timeline_media", "edge_followed_by", "username", "shortcode", "full_name"]:
                    results.append((current_path, k, str(v)[:200]))
                scan(v, current_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                scan(item, f"{path}[{idx}]")
                
    scan(data)
    
    print(f"Found {len(results)} matches:")
    for path, key, val_preview in results[:20]:
        print(f"- Path: {path}")
        print(f"  Key: {key}")
        print(f"  Value: {val_preview}")

if __name__ == "__main__":
    analyze_facebook_json()
