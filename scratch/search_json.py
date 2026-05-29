import os
import json

def search_json_files():
    print("Searching generated json files for profile or post data...")
    for filename in sorted(os.listdir("scratch")):
        if filename.startswith("json_tag_") and filename.endswith(".json"):
            filepath = os.path.join("scratch", filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Check for telltale keys
                data_str = json.dumps(data)
                
                # Search for keywords
                has_nasa = "nasa" in data_str.lower()
                has_biography = "biography" in data_str
                has_edge = "edge_owner_to_timeline_media" in data_str or "edge_followed_by" in data_str
                has_xdt = "xdt_api__v1__users__web_profile_info" in data_str
                
                if has_edge or has_biography or has_xdt:
                    print(f"\n[FOUND MATCH] {filename}:")
                    print(f"- Size: {os.path.getsize(filepath)} bytes")
                    print(f"- Contains 'biography': {has_biography}")
                    print(f"- Contains 'edge_owner_to_timeline_media': {'edge_owner_to_timeline_media' in data_str}")
                    print(f"- Contains 'xdt_api__v1__users__web_profile_info': {has_xdt}")
                    
                    # Print top-level keys
                    if isinstance(data, dict):
                        print(f"- Top-level keys: {list(data.keys())}")
                        # Let's inspect some nested keys if they exist
                        if "require" in data:
                            print(f"- Inside 'require': {str(data['require'])[:200]}...")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    search_json_files()
