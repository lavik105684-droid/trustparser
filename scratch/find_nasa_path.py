import json

def find_nasa_path():
    filepath = "scratch/json_tag_13.json"
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("Finding paths to 'nasa' inside json_tag_13.json...")
    
    results = []
    
    def scan(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                current_path = f"{path}.{k}" if path else k
                if "nasa" in str(k).lower():
                    results.append((current_path, "KEY", str(k)))
                scan(v, current_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                scan(item, f"{path}[{idx}]")
        elif isinstance(obj, str):
            if "nasa" in obj.lower():
                results.append((path, "STRING", obj))
                
    scan(data)
    
    print(f"Found {len(results)} matches:")
    for path, match_type, val in results[:30]:
        print(f"- Path: {path} ({match_type})")
        print(f"  Value: {val[:200]}")

if __name__ == "__main__":
    find_nasa_path()
