import subprocess
import sys

# Reconfigure stdout/stderr to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

NLM_PATH = r"C:\Users\lavik\AppData\Roaming\Python\Python314\Scripts\nlm.exe"

def test():
    cmd = [NLM_PATH, "source", "add", "f0a9b330-ed06-41ff-a4c3-efe58b03430f", "--youtube", "https://www.youtube.com/watch?v=uz_3dSU8rQo", "--wait"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    print("Returncode:", res.returncode)
    print("Stdout:", res.stdout)
    print("Stderr:", res.stderr)

if __name__ == "__main__":
    test()
