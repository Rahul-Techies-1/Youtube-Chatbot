# ==========================================================
# Imports
# ==========================================================

import os
from urllib.parse import urlparse, parse_qs
from groq import Groq
from dotenv import load_dotenv
import streamlit as st

from youtube_transcript_api import YouTubeTranscriptApi

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from huggingface_hub import InferenceClient

# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()

# ==========================================================
# Global Variables
# ==========================================================

vector_store = None
retriever = None
llm = None

# ==========================================================
# Extract Video ID
# ==========================================================

def extract_video_id(url: str):

    parsed = urlparse(url)

    if parsed.hostname in [
        "www.youtube.com",
        "youtube.com"
    ]:
        return parse_qs(parsed.query)["v"][0]

    elif parsed.hostname == "youtu.be":
        return parsed.path[1:]

    else:
        raise ValueError("Invalid YouTube URL")


# ==========================================================
# Download Transcript
# ==========================================================

def get_transcript(video_id):

    ytt = YouTubeTranscriptApi()

    try:

        transcript = ytt.fetch(
            video_id,
            languages=["hi", "en"]
        )

    except Exception as e:

        print(f"Preferred language retrieval failed: {e}")

        transcript = ytt.fetch(
            video_id
        )

    text = " ".join(
        snippet.text
        for snippet in transcript
    )

    return text

# ==========================================================
# Process Video
# ==========================================================

def process_video(video_url):

    global vector_store
    global retriever
    global llm

    # ----------------------------------------
    # Video ID
    # ----------------------------------------

    video_id = extract_video_id(video_url)

    # ----------------------------------------
    # Transcript
    # ----------------------------------------

    transcript = get_transcript(video_id)

    print("Transcript Downloaded Successfully")

    # ----------------------------------------
    # LangChain Document
    # ----------------------------------------

    documents = [

        Document(
            page_content=transcript,
            metadata={
                "video_id": video_id
            }
        )

    ]

    # ----------------------------------------
    # Split into Chunks
    # ----------------------------------------

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=1000,
        chunk_overlap=200

    )

    chunks = splitter.split_documents(documents)

    print(f"Chunks Created : {len(chunks)}")

    # ----------------------------------------
    # Embedding Model
    # ----------------------------------------

    embeddings = HuggingFaceEmbeddings(

        model_name="BAAI/bge-small-en-v1.5"

    )

    # ----------------------------------------
    # Chroma Vector Store
    # ----------------------------------------

    vector_store = Chroma.from_documents(

        documents=chunks,

        embedding=embeddings

    )

    # ----------------------------------------
    # Retriever
    # ----------------------------------------

    retriever = vector_store.as_retriever(

        search_kwargs={

            "k": 4

        }

    )

    # ----------------------------------------
    # HuggingFace Client
    # ----------------------------------------

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            raise ValueError(
                "GROQ_API_KEY is missing. Please configure it in your .env file or Streamlit Secrets."
            )
    llm = Groq(
        api_key=api_key
    )

    print("✅ Video Processed Successfully")

# ==========================================================
# Ask Question
# ==========================================================

def ask_with_sources(question):

    global retriever
    global llm

    if retriever is None:
        raise Exception(
            "Please process a YouTube video first."
        )

    # -------------------------------------------------
    # Retrieve Relevant Chunks
    # -------------------------------------------------

    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # -------------------------------------------------
    # Prompt
    # -------------------------------------------------

    prompt = f"""
You are an intelligent AI YouTube Assistant.

Your task is to answer ONLY from the provided transcript.

Rules:

1. Never make up information.

2. If the answer is not available in the transcript,
reply exactly:

"I couldn't find that information in the video."

3. Answer in simple English.

4. Keep answers concise unless user asks for details.

-------------------------
VIDEO TRANSCRIPT
-------------------------

{context}

-------------------------
USER QUESTION
-------------------------

{question}

-------------------------
ANSWER
-------------------------
"""

    # -------------------------------------------------
    # Hugging Face Chat Completion
    # -------------------------------------------------

    response = llm.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {
                "role": "system",
                "content":
                "You are a helpful AI assistant that answers only from the provided transcript."
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.3,

        max_tokens=512

    )

    answer = response.choices[0].message.content.strip()

    # -------------------------------------------------
    # Sources
    # -------------------------------------------------

    sources = []

    for i, doc in enumerate(docs, start=1):

        sources.append(
            {
                "chunk": i,
                "content": doc.page_content
            }
        )

    return answer, sources