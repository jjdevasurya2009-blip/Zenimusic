import re, random, asyncio
from datetime import timedelta
from typing import Optional

SMALL_CAPS_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
    'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
}

class Helpers:
    @staticmethod
    def to_smallcaps(text: str) -> str:
        result = []
        for ch in text:
            lower = ch.lower()
            result.append(SMALL_CAPS_MAP.get(lower, ch))
        return "".join(result)

    @staticmethod
    def format_msg(text: str, quote: bool = True) -> str:
        parts = re.split(r'(<[^>]+>)', text)
        converted = []
        for part in parts:
            if part.startswith('<') and part.endswith('>'):
                converted.append(part)
            else:
                converted.append(Helpers.to_smallcaps(part))
        result = "".join(converted)
        if quote and "<blockquote>" not in result:
            result = f"<blockquote>{result}</blockquote>"
        return result

    @staticmethod
    async def reply_formatted(message, text: str, **kwargs):
        formatted = Helpers.format_msg(text)
        return await message.reply(formatted, **kwargs)

    @staticmethod
    async def edit_formatted(message, text: str, **kwargs):
        formatted = Helpers.format_msg(text)
        return await message.edit(formatted, **kwargs)

    @staticmethod
    def format_time(seconds):
        return str(timedelta(seconds=int(seconds)))

    @staticmethod
    def parse_seconds(s):
        p = r'(?:(\d+):)?(\d+):(\d+)'
        m = re.match(p, s)
        if m:
            h = int(m.group(1)) if m.group(1) else 0
            return h*3600 + int(m.group(2))*60 + int(m.group(3))
        p2 = r'(\d+)([smh])'
        m2 = re.match(p2, s)
        if m2:
            v = int(m2.group(1))
            u = m2.group(2)
            return v * {'s':1,'m':60,'h':3600}[u]
        return 0

    @staticmethod
    def progress(progress, length=10):
        filled = int(progress * length)
        return "▓" * filled + "░" * (length - filled)

    @staticmethod
    def format_number(n):
        if n >= 10000000: return f"{n/10000000:.1f}Cr"
        if n >= 100000: return f"{n/100000:.1f}L"
        if n >= 1000: return f"{n/1000:.1f}K"
        return str(n)

    @staticmethod
    def sanitize(text):
        return re.sub(r'[<>]', '', text)[:200]

    @staticmethod
    def extract_url(text):
        m = re.search(r'https?://[^\s]+', text)
        return m.group(0) if m else None

    @staticmethod
    def random_emoji():
        emojis = ["🎵","🎶","🎸","🎹","🎺","🎻","🥁","🎤","🎧","📻","🎼","🎷","🎙","🎛","🎚","🎬"]
        return random.choice(emojis)

    @staticmethod
    def interactive_leave():
        msgs = [
            "😢 No one is hearing my melodious voice... Leaving!",
            "💔 Playing to an empty room... I'm out!",
            "👋 Guess nobody's vibing. See ya!",
            "🎵 My music is too fire for an empty VC!",
            "🚶‍♂️ Walking out... literally no one's here!",
            "😔 Playing for ghosts... time to bounce!",
            "🎤 Drops mic. Leaves empty room.",
            "💀 Dead air detected. I'm gone!",
            "👻 Only ghosts are jamming here. Later!",
            "🔇 Silence is golden but I'm not. Bye!"
        ]
        return random.choice(msgs)

    @staticmethod
    def playing_emojis():
        return random.choice(["▶️","🎵","🎶","🎼","🎧","🔥","✨","💫","🌟","⚡"])

    @staticmethod
    def reaction_dice():
        return random.choice(["🎲","🎯","🎳","🎰","🎪"])
