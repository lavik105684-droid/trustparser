import json

def inspect_tag_json():
    with open("scratch/logged_in_tag_13.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("Inspecting scratch/logged_in_tag_13.json structure...")
    
    # Let's search recursively for biography to see its exact path and surroundings
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
                
    find_key(data, "biography")
    print(f"\nFound {len(paths)} biography instances:")
    for path, val in paths:
        print(f"Path: {path}")
        print(f"Value: {repr(val)}")
        
    paths_posts = []
    find_key(data, "edge_owner_to_timeline_media")
    print(f"\nFound {len(paths_posts)} edge_owner_to_timeline_media instances:")
    for path, val in paths_posts:
        print(f"Path: {path}")
        if isinstance(val, dict):
            print(f"Keys: {list(val.keys())}")
            count = val.get("count")
            edges = val.get("edges", [])
            print(f"Count: {count}, Edges count: {len(edges)}")
            if edges:
                print(f"First post preview keys: {list(edges[0]['node'].keys())}")
                
if __name__ == "__main__":
    inspect_tag_json()
