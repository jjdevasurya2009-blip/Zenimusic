import os, json
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    STRING_SESSION = os.getenv("STRING_SESSION", "")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", 0))
    BOT_NAME = "zenii X music"
    BOT_USERNAME = "zenii_X_music_bot"
    VERSION = "2.0.0"
    DEFAULT_PLAYLIST_LIMIT = 50
    PREMIUM_PLAYLIST_LIMIT = 200
    DEFAULT_VOLUME = 100
    MAX_QUEUE = 20
    PREMIUM_MAX_QUEUE = 50
    SUPPORT_URL = "https://t.me/zenii_support"
    UPDATES_URL = "https://t.me/zenii_updates"
    REACTION_EMOJI = "🎵"
    STARTUP_TEXT = "✧ ZENII X MUSIC ✧"
