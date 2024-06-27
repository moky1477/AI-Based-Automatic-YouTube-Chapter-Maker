import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
import streamlit as st
import re
import csv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import google.generativeai as genai 
import os

load_dotenv()

# Configure the Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for the generative AI
prompt = """
You create labeled chapters for youtube videos about Programming. The transcript you will be given 
has a timestamp on one line and the next line is the corresponding text for that timestamp. 
This repeats for the whole transcript. 
The output should be each timestamp and chapter title on a newline. 
Each chapter title should be no longer than 50 characters. 
The chapter titles can be keywords, summarized concepts, or titles. 
Only create a new chapter when the topic changes significantly. 
At least 2 minutes should have elapsed before specifying a new chapter. 
Only use the timestamps specified in the transcript. 
The chapter timestamps should not be greater than the largest timestamp in the transcript. 
The output for each line should look like: 
Chapter 1: 00:00 - Title
Chapter 2: 02:00 - Title
Each chapter should be on a new line.
"""

# API_KEY = os.getenv('API KEY')

# Extract the video_id from the given URL
def get_video_id(url):
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return video_id_match.group(1) if video_id_match else None

# Function to convert seconds to hh:mm:ss format
def convert_seconds(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hrs:02}:{mins:02}:{secs:02}"

# Function to get the transcript data from YouTube videos
def extract_transcript_details(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ""
        for item in transcript_list:
            timestamp = convert_seconds(item['start'])
            transcript += f"{timestamp}\n{item['text']}\n"
        return transcript
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Function to generate the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript)
    return response.text

# Streamlit UI
st.title('Automatic YouTube Chapter Maker')
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = get_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
        # st.write(get_video_title(video_id))
    else:
        st.error("Invalid YouTube URL")

if st.button("Make Chapters"):
    if youtube_link:
        video_id = get_video_id(youtube_link)
        if video_id:
            transcript_text = extract_transcript_details(video_id)
            if transcript_text:
                summary = generate_gemini_content(transcript_text, prompt)
                st.markdown("## Detailed Chapters:")
                for line in summary.splitlines():
                    st.write(line)
            else:
                st.error("Could not retrieve transcript")
        else:
            st.error("Invalid YouTube URL")
    else:
        st.error("Please enter a YouTube link")
