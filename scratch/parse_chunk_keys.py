import json

def test():
    with open("scratch/chunk.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    
    print("Keys in videoRenderer:")
    for k in data.keys():
        print(f"- {k}: {str(data[k])[:100]}")
        
    with open("scratch/chunk_pretty.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved pretty JSON to scratch/chunk_pretty.json")

if __name__ == "__main__":
    test()
