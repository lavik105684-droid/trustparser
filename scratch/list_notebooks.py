import subprocess
import sys

# Reconfigure stdout/stderr to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

NLM_PATH = r"C:\Users\lavik\AppData\Roaming\Python\Python314\Scripts\nlm.exe"

def test():
    cmd = [NLM_PATH, "notebook", "list"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    print("Returncode:", res.returncode)
    print("Stdout:")
    print(res.stdout)
    print("Stderr:")
    print(res.stderr)

if __name__ == "__main__":
    test()
