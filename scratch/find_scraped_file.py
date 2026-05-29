import os

def find_file():
    print("Searching for scraped_examples_raw.json on the system...")
    found = False
    # Walk modest-carson and brain app data
    for path in ["C:\\Users\\lavik\\Documents\\antigravity\\modest-carson", "C:\\Users\\lavik\\.gemini\\antigravity"]:
        for root, dirs, files in os.walk(path):
            if "scraped_examples_raw.json" in files:
                print(f"Found in: {os.path.join(root, 'scraped_examples_raw.json')}")
                found = True
    if not found:
        print("Not found anywhere.")

if __name__ == "__main__":
    find_file()
