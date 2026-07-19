import re
from pytube import YouTube


# ======================================================
# Validate YouTube URL
# ======================================================

def is_valid_youtube_url(url: str) -> bool:
    """
    Returns True if the URL is a valid YouTube URL.
    """

    pattern = (
        r"(https?://)?(www\.)?"
        r"(youtube\.com|youtu\.be)/.+"
    )

    return re.match(pattern, url) is not None


# ======================================================
# Extract Video ID
# ======================================================

def extract_video_id(url: str):

    """
    Extracts the YouTube Video ID.
    """

    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]

    if "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]

    return None


# ======================================================
# Thumbnail URL
# ======================================================

def get_thumbnail(video_url):

    """
    Returns thumbnail URL.
    """

    video_id = extract_video_id(video_url)

    if video_id:

        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    return None


# ======================================================
# Format Duration
# ======================================================

def format_duration(seconds):

    minutes = seconds // 60

    seconds = seconds % 60

    return f"{minutes}:{seconds:02d}"


# ======================================================
# Video Information
# ======================================================

def get_video_info(video_url):

    """
    Returns
    Title
    Author
    Length
    Views
    Publish Date
    Thumbnail
    """

    try:

        yt = YouTube(video_url)

        info = {

            "title": yt.title,

            "author": yt.author,

            "length": format_duration(yt.length),

            "views": f"{yt.views:,}",

            "thumbnail": yt.thumbnail_url,

            "publish_date": yt.publish_date.strftime("%d-%m-%Y")

        }

        return info

    except Exception:

        return None


# ======================================================
# Processing Messages
# ======================================================

def processing_steps():

    return [

        "📥 Downloading Transcript...",

        "✂ Splitting Transcript...",

        "🧠 Creating Embeddings...",

        "💾 Building ChromaDB...",

        "🤖 Initializing LLM...",

        "✅ Ready!"

    ]


# ======================================================
# Suggested Questions
# ======================================================

def suggested_questions():

    return [

        "Summarize this video",

        "Explain the main concepts",

        "Give me key takeaways",

        "What are the important points?",

        "Create interview questions",

        "Generate quiz questions",

        "Explain like I'm a beginner"

    ]