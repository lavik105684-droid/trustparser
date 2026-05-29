import subprocess
import traceback
import sys

NLM_PATH = r"C:\Users\lavik\AppData\Roaming\Python\Python314\Scripts\nlm.exe"

def test():
    cmd = [NLM_PATH, "source", "--debug", "add", "YouTube_AI_Factory_Vault", "--youtube", "https://www.youtube.com/watch?v=uz_3dSU8rQo", "--wait"]
    print("Running command:", " ".join(cmd))
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        print("Success! Returncode:", res.returncode)
        print("Stdout length:", len(res.stdout))
        print("Stderr length:", len(res.stderr))
    except Exception as e:
        print("Exception caught:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
