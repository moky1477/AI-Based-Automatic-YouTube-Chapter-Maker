import re
import csv
import pandas as pd
from googleapiclient.discovery import build
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi

API_KEY = 'AIzaSyDaSH0H2Xmyx-kJQscP4i0H38Vh18CDksE'

# Extract the video_id from the given URL
def get_video_id(url):
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return video_id_match.group(1) if video_id_match else None

# Extract the video title from youtube videos
def get_video_title(video_id):
    # build the youTube service
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # fetch the video details
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    response = request.execute()

    # extract the title
    title = response['items'][0]['snippet']['title'] if response['items'] else 'Unknown Title'
    return title


# Function to extract transcript details from a YouTube URL
def extract_transcript_details(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        st.error("Error extracting transcript: " + str(e))
        return None
    
# Save the transcript to a CSV file
def save_to_csv(title, transcript, filename):
    # save the title and transcript to a CSV file
    transcript_data = [{'start': entry['start'], 'text': entry['text']} for entry in transcript]
    df = pd.DataFrame(transcript_data)
    df.to_csv(filename, index=False)

    # save the title separately
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title:', title])

def main():
    url = input('Enter the YouTube video link: ')
    video_id = get_video_id(url)

    if not video_id:
        print('Invalid YouTube URL.')
        return

    title = get_video_title(video_id)
    transcript = extract_transcript_details(video_id)

    if not transcript:
        print('No transcript available for this video.')
        return

    filename = f"{video_id}_transcript.csv"
    save_to_csv(title, transcript, filename)
    print(f'Transcript saved to {filename}')

if __name__ == '__main__':
    main()