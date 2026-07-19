import streamlit as st
import time

from rag import process_video, ask_with_sources

from utils import (
    get_thumbnail,
    get_video_info,
    processing_steps,
    is_valid_youtube_url
)

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------

st.set_page_config(
    page_title="YouTube AI Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------
# LOAD CSS
# -------------------------------------------------------

def load_css():
    try:
        with open("style.css") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    except:
        pass

load_css()

# -------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "video_processed" not in st.session_state:
    st.session_state.video_processed = False

if "video_url" not in st.session_state:
    st.session_state.video_url = ""

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------

with st.sidebar:

    st.title("🎥 YouTube AI")

    st.markdown("---")

    if st.button("➕ New Chat", use_container_width=True):

        st.session_state.messages = []

        st.session_state.video_processed = False

        st.rerun()

    st.markdown("---")

    st.subheader("Tech Stack")

    st.success("🐍 Python")

    st.success("🦜 LangChain")

    st.success("🤗 HuggingFace")

    st.success("🧠 RAG")

    st.success("📦 ChromaDB")

    st.success("🎈 Streamlit")

    st.markdown("---")

    st.info(
        """
Built with ❤️

AI Powered

Retrieval Augmented Generation

Chat with any YouTube Video
"""
    )

# -------------------------------------------------------
# HEADER
# -------------------------------------------------------

st.title("🎥 YouTube AI Assistant")

st.caption(
    "Chat with any YouTube video using RAG + HuggingFace + ChromaDB"
)

st.divider()

# -------------------------------------------------------
# URL INPUT
# -------------------------------------------------------

video_url = st.text_input(
    "Paste YouTube URL",
    placeholder="https://www.youtube.com/watch?v=..."
)

# -------------------------------------------------------
# VALIDATION
# -------------------------------------------------------

if video_url:

    if not is_valid_youtube_url(video_url):

        st.error("Invalid YouTube URL")

        st.stop()

# -------------------------------------------------------
# VIDEO INFO
# -------------------------------------------------------

if video_url:

    info = get_video_info(video_url)

    thumbnail = get_thumbnail(video_url)

    col1, col2 = st.columns([1,2])

    with col1:

        if thumbnail:

            st.image(
                thumbnail,
                use_column_width=True
            )

    with col2:

        if info:
            st.subheader(info["title"])

            st.caption(f"👤 {info['author']}")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Duration",
                info["length"]
            )

            c2.metric(
                "Views",
                info["views"]
            )

            c3.metric(
                "Published",
                info["publish_date"]
            )

st.divider()

# -------------------------------------------------------
# PROCESS BUTTON
# -------------------------------------------------------

if st.button(
    "🚀 Process Video",
    use_container_width=True
):

    if video_url == "":

        st.warning("Please enter a YouTube URL.")

    else:

        progress = st.progress(0)

        status = st.empty()

        steps = processing_steps()

        for i, step in enumerate(steps):

            status.info(step)

            progress.progress(
                int((i + 1) * 100 / len(steps))
            )

            time.sleep(0.8)

        process_video(video_url)

        st.session_state.video_processed = True

        st.success("Video processed successfully!")

        st.balloons()

st.divider()
# -------------------------------------------------------
# SUGGESTED QUESTIONS
# -------------------------------------------------------

if st.session_state.video_processed:

    st.subheader("✨ Suggested Questions")

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("📄 Summarize"):
        st.session_state.selected_prompt = "Summarize the complete video."

    if col2.button("🧠 Key Points"):
        st.session_state.selected_prompt = "What are the key points discussed?"

    if col3.button("❓ Quiz Me"):
        st.session_state.selected_prompt = "Generate 5 interview questions from this video."

    if col4.button("📚 Explain"):
        st.session_state.selected_prompt = "Explain the concepts like I'm a beginner."

st.divider()

# -------------------------------------------------------
# CHAT HISTORY
# -------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------------------------------------
# CHAT INPUT
# -------------------------------------------------------

if st.session_state.video_processed:

    default_prompt = st.session_state.get("selected_prompt", "")

    prompt = st.chat_input(
        "Ask anything about this YouTube video..."
    )

    if default_prompt and not prompt:
        prompt = default_prompt
        st.session_state.selected_prompt = ""

    if prompt:

        # ---------------- USER MESSAGE ----------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        # ---------------- AI MESSAGE ----------------

        with st.chat_message("assistant"):

            with st.spinner("🤖 AI is thinking..."):

                answer, sources = ask_with_sources(prompt)

                st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        # ---------------- SOURCES ----------------

        with st.expander("📚 Retrieved Source Chunks"):

            if len(sources) == 0:

                st.warning("No sources found.")

            else:

                for index, chunk in enumerate(sources):

                    st.markdown(f"### 📄 Chunk {index+1}")

                    st.write(chunk)

                    st.divider()

st.divider()

# -------------------------------------------------------
# CHAT STATISTICS
# -------------------------------------------------------

if st.session_state.video_processed:

    st.subheader("📊 Chat Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Messages",
        len(st.session_state.messages)
    )

    assistant_messages = len(
        [m for m in st.session_state.messages if m["role"] == "assistant"]
    )

    col2.metric(
        "AI Responses",
        assistant_messages
    )

    user_messages = len(
        [m for m in st.session_state.messages if m["role"] == "user"]
    )

    col3.metric(
        "Questions Asked",
        user_messages
    )

st.divider()

# -------------------------------------------------------
# DOWNLOAD CHAT
# -------------------------------------------------------

if st.session_state.video_processed:

    conversation = ""

    for msg in st.session_state.messages:

        role = msg["role"].capitalize()

        conversation += f"{role}:\n"

        conversation += msg["content"]

        conversation += "\n\n"

    st.download_button(
        label="📥 Download Conversation",
        data=conversation,
        file_name="chat_history.txt",
        mime="text/plain",
        use_container_width=True
    )

st.divider()

# -------------------------------------------------------
# CLEAR CHAT
# -------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.success("Conversation cleared.")

        st.rerun()

with col2:

    if st.button(
        "🔄 Process Another Video",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.video_processed = False

        st.rerun()

st.divider()

# -------------------------------------------------------
# ABOUT PROJECT
# -------------------------------------------------------

with st.expander("ℹ️ About This Project"):

    st.markdown("""
### 🎥 YouTube AI Assistant

This application lets you chat with any YouTube video using a
Retrieval-Augmented Generation (RAG) pipeline.

### 🚀 Workflow

1. Paste YouTube URL
2. Extract Transcript
3. Split into Chunks
4. Generate Embeddings
5. Store in ChromaDB
6. Retrieve Relevant Chunks
7. Generate Answer using Hugging Face LLM

### 🛠️ Tech Stack

- Python
- Streamlit
- LangChain
- Hugging Face Endpoint
- Hugging Face Embeddings
- ChromaDB
- RAG
""")

st.divider()

# -------------------------------------------------------
# PROJECT METRICS
# -------------------------------------------------------

st.subheader("📈 Project Overview")

m1, m2, m3, m4 = st.columns(4)

m1.metric("LLM", "Qwen 2.5")

m2.metric("Embedding", "BGE")

m3.metric("Vector DB", "Chroma")

m4.metric("Framework", "LangChain")

st.divider()

# -------------------------------------------------------
# FOOTER
# -------------------------------------------------------

st.markdown(
"""
<hr>

<div style="text-align:center">

<h3>🎥 YouTube AI Assistant</h3>

<p>
Built using ❤️ with
<b>Streamlit</b> •
<b>LangChain</b> •
<b>ChromaDB</b> •
<b>Hugging Face</b>
</p>

<p style="color:gray;">
Developed by Rahul
</p>

</div>
""",
unsafe_allow_html=True
)