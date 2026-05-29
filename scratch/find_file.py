import os

def find_file():
    print("Searching for picuki_profile.html in C:\\Users\\lavik\\Documents\\antigravity\\modest-carson...")
    found = False
    for root, dirs, files in os.walk("C:\\Users\\lavik\\Documents\\antigravity\\modest-carson"):
        if "picuki_profile.html" in files:
            print(f"Found in: {os.path.join(root, 'picuki_profile.html')}")
            found = True
    if not found:
        print("Not found in modest-carson.")
        
    print("\nSearching in app data brain directory...")
    for root, dirs, files in os.walk("C:\\Users\\lavik\\.gemini\\antigravity\\brain\\4b2333aa-7ee4-4292-bb8d-d76aaab77e33"):
        if "picuki_profile.html" in files:
            print(f"Found in: {os.path.join(root, 'picuki_profile.html')}")
            found = True

if __name__ == "__main__":
    find_file()
