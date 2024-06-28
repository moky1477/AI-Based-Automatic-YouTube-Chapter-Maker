import os
import re
from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import google.generativeai as genai 

load_dotenv()

# Configure the Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

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

# Function to extract the video_id from the given URL
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
        return str(e)

# Function to generate the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript)
    return response.text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/make_chapters', methods=['POST'])
def make_chapters():
    youtube_link = request.form.get('youtube_link')
    if youtube_link:
        video_id = get_video_id(youtube_link)
        if video_id:
            transcript_text = extract_transcript_details(video_id)
            if transcript_text:
                summary = generate_gemini_content(transcript_text, prompt)
                chapters = summary.splitlines()
                return jsonify({'chapters': chapters})
            else:
                return jsonify({'error': 'Could not retrieve transcript'})
        else:
            return jsonify({'error': 'Invalid YouTube URL'})
    else:
        return jsonify({'error': 'Please enter a YouTube link'})

if __name__ == '__main__':
    app.run(debug=True)
