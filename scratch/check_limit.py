import json
import os

transcript_path = r"C:\Users\lavik\.gemini\antigravity\brain\4b2333aa-7ee4-4292-bb8d-d76aaab77e33\.system_generated\logs\transcript.jsonl"

def analyze_transcript():
    if not os.path.exists(transcript_path):
        print(f"Transcript not found at {transcript_path}")
        return
        
    line_count = 0
    steps = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line_count += 1
            try:
                steps.append(json.loads(line))
            except Exception as e:
                pass
                
    print(f"Total steps in transcript: {line_count}")
    print(f"Loaded successfully: {len(steps)}")
    
    if steps:
        last_step = steps[-1]
        print(f"Last step index: {last_step.get('step_index')}")
        print(f"Last step type: {last_step.get('type')}")
        print(f"Last step source: {last_step.get('source')}")

if __name__ == "__main__":
    analyze_transcript()
