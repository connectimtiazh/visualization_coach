import os

# API Keys (retrieved from Replit Secrets)
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
AIRTABLE_BASE_ID = os.environ['AIRTABLE_BASE_ID']

# Airtable configuration
AIRTABLE_TABLE_NAME = 'User'

# Audio file storage configuration
AUDIO_STORAGE_PATH = '/tmp/audio_files'

# Customize the TTS voice
TTS_VOICE = 'nova'

# Background music file path
BACKGROUND_MUSIC_PATH = 'background_music.mp3'

# Audio overlay settings
BACKGROUND_VOLUME_REDUCTION = 10  # in dB
REPLIT_BASE_URL = "https://visualization-coach-instagptmarketi.replit.app/"
