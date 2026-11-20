from youtube_transcript_api import YouTubeTranscriptApi

video_id = "nlz9j-r0U9U"

ytt = YouTubeTranscriptApi()

try:
    transcript = ytt.fetch(video_id, languages=["hi"])

    text = " ".join(
        snippet.text for snippet in transcript
    )

    print("Transcript retrieved successfully!")
    print(text[:2000])

except Exception as e:
    print("Transcript retrieval failed:")
    print(type(e).__name__)
    print(e)