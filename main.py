import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from pydub import AudioSegment
from openai import OpenAI
import io
from pyairtable import Table
from config import *

app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)
airtable = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)

def add_pauses(text):
    text = text.replace('. ', '......... ')
    text = text.replace(', ', '..... ')
    pause_phrases = ['Take a deep breath', 'Relax', 'Feel', 'Imagine']
    for phrase in pause_phrases:
        text = text.replace(f'{phrase}', f'{phrase}...... ')
    return text

def generate_audio(text):
    try:
        text_with_pauses = add_pauses(text)
        response = client.audio.speech.create(
            model="tts-1",
            voice=TTS_VOICE,
            input=text_with_pauses
        )
        return io.BytesIO(response.content)
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        return None

def process_audio(audio_content):
    try:
        speech = AudioSegment.from_mp3(audio_content)
        background = AudioSegment.from_mp3(BACKGROUND_MUSIC_PATH)

        background = background * (len(speech) // len(background) + 1)
        background = background[:len(speech)]
        background = background - BACKGROUND_VOLUME_REDUCTION

        final_audio = speech.overlay(background)

        silence = AudioSegment.silent(duration=2000)
        final_audio = silence + final_audio + silence

        filename = f"{uuid.uuid4()}.mp3"
        file_path = os.path.join(AUDIO_STORAGE_PATH, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        final_audio.export(file_path, format="mp3")

        full_audio_url = f"{REPLIT_BASE_URL}/audio/{filename}"
        return full_audio_url
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return None

def create_airtable_record(name, email, audio_link):
    try:
        record = airtable.create({
            "Name": name,
            "Email": email,
            "audio_link": audio_link
        })
        return record
    except Exception as e:
        print(f"Error creating Airtable record: {str(e)}")
        return None

@app.route('/generate_audio', methods=['POST'])
def generate_visualization_audio():
    data = request.json
    if not data or 'script' not in data:
        return jsonify({"error": "No script provided"}), 400

    script = data['script']
    audio_content = generate_audio(script)
    if not audio_content:
        return jsonify({"error": "Failed to generate audio"}), 500

    full_audio_url = process_audio(audio_content)
    if not full_audio_url:
        return jsonify({"error": "Failed to process audio"}), 500

    return jsonify({"audio_link": full_audio_url}), 200

@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.json
    if not data or 'name' not in data or 'email' not in data or 'audio_link' not in data:
        return jsonify({"error": "Missing required information"}), 400

    name = data['name']
    email = data['email']
    audio_link = data['audio_link']

    record = create_airtable_record(name, email, audio_link)
    if not record:
        return jsonify({"error": "Failed to create Airtable record"}), 500

    return jsonify({
        "message": "Congratulations! You are now ready for the 7 day visualization challenge",
        "record_id": record['id']
    }), 200

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_STORAGE_PATH, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)