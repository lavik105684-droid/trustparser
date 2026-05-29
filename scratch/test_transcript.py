from youtube_transcript_api import YouTubeTranscriptApi
import sys

def test():
    video_id = "8wGjsRASSIo"  # The ID of the first video returned in our search test!
    print(f"Attempting to fetch transcript for video: {video_id}")
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=['ru', 'en'])
        raw_data = transcript.to_raw_data()
        full_text = " ".join([item['text'] for item in raw_data])
        print(f"[SUCCESS] Transcript length: {len(full_text)} characters")
        print(f"Snippet: {full_text[:200]}...")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fetch: {e}")
        return False

if __name__ == "__main__":
    test()
