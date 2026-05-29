import urllib.request
import urllib.error
import sys

endpoints = [
    "http://localhost:5678",
    "http://127.0.0.1:5678",
    "http://10.0.2.2:5678",
    "http://host.docker.internal:5678"
]

print("=== STARTING n8n HEALTH CHECK PROBE ===")
any_success = False

for ep in endpoints:
    print(f"Probing {ep}... ", end="", flush=True)
    try:
        req = urllib.request.Request(ep, method="GET")
        with urllib.request.urlopen(req, timeout=3) as res:
            code = res.getcode()
            print(f"SUCCESS (HTTP {code})")
            any_success = True
    except urllib.error.HTTPError as e:
        print(f"RESPONDED WITH HTTP {e.code}")
        any_success = True
    except Exception as e:
        print(f"FAILED ({type(e).__name__})")

print("\n=== PROBE RESULTS SUMMARY ===")
if any_success:
    print("STATUS: n8n server is responding!")
    sys.exit(0)
else:
    print("STATUS: n8n server is completely OFFLINE.")
    sys.exit(1)
