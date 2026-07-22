import os, random, asyncio
from typing import Optional, Dict, List
from pyrogram import Client
from yt_dlp import YoutubeDL
from database.mongo import MongoDB
from music.calls import VoiceHandler
from utils.logger import Logger
from utils.helpers import Helpers
from config import Config

class MusicPlayer:
    def __init__(self, bot: Client, voice: VoiceHandler, db: MongoDB):
        self.bot = bot
        self.voice = voice
        self.db = db
        self.log = Logger()
        self.h = Helpers()
        self.queues: Dict[int, List[Dict]] = {}
        self.current: Dict[int, Optional[Dict]] = {}
        self.loop: Dict[int, bool] = {}
        self.volumes: Dict[int, int] = {}
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True, 'no_warnings': True,
            'extract_flat': False,
            'user_agent': 'Mozilla/5.0',
        }
        self.ydl_video = {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'quiet': True, 'no_warnings': True,
            'extract_flat': False,
        }
        self.radio_stations = {
            "jazz": "https://streams.fluxfm.de/Jazzmeile/mp3-128/",
            "rock": "https://streams.fluxfm.de/rock/mp3-128/",
            "chill": "https://streams.fluxfm.de/chillhop/mp3-128/",
            "lofi": "https://streams.fluxfm.de/lofi/mp3-128/",
            "classical": "https://streams.fluxfm.de/klassik/mp3-128/",
            "pop": "https://streams.fluxfm.de/pop/mp3-128/",
            "edm": "https://streams.fluxfm.de/electro/mp3-128/",
            "r&b": "https://streams.fluxfm.de/rnb/mp3-128/",
            "hiphop": "https://streams.fluxfm.de/hiphop/mp3-128/",
            "country": "https://streams.fluxfm.de/country/mp3-128/",
        }

    async def extract(self, query: str, video: bool = False) -> Optional[Dict]:
        try:
            opts = self.ydl_video if video else self.ydl_opts
            with YoutubeDL(opts) as ydl:
                if query.startswith(('http://', 'https://')):
                    info = ydl.extract_info(query, download=False)
                else:
                    info = ydl.extract_info(f"ytsearch:{query}", download=False)
                    if 'entries' in info and info['entries']:
                        info = info['entries'][0]
                is_live = info.get('is_live', False) or info.get('live_status') == 'is_live'
                return {
                    'id': info.get('id', ''),
                    'title': info.get('title', 'Unknown'),
                    'url': info.get('url', ''),
                    'webpage_url': info.get('webpage_url', ''),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'artist': info.get('artist', info.get('uploader', 'Unknown')),
                    'source': 'youtube',
                    'is_live': is_live,
                    'requested_by': 0
                }
        except Exception as e:
            self.log.error(f"Extract error: {e}")
            return None

    async def play_song(self, chat_id: int, query: str, user_id: int=0, video: bool=False):
        info = await self.extract(query, video)
        if not info: return None
        info['requested_by'] = user_id
        if chat_id not in self.queues:
            self.queues[chat_id] = []
        qlimit = await self.db.get_queue_size(user_id)
        if len(self.queues[chat_id]) >= qlimit:
            return "queue_full"
        self.queues[chat_id].append(info)
        if chat_id not in self.current or not self.current[chat_id]:
            return await self._play_next(chat_id)
        return info

    async def play_radio(self, chat_id: int, station: str):
        url = self.radio_stations.get(station.lower())
        if not url:
            return None
        self.current[chat_id] = {"type": "radio", "title": f"📻 {station.title()} Radio",
                                  "url": url, "artist": "Radio", "duration": 0,
                                  "thumbnail": "", "is_live": True}
        await self.voice.join_radio(chat_id, url)
        return self.current[chat_id]

    async def play_live(self, chat_id: int, query: str):
        info = await self.extract(query, video=True)
        if not info: return None
        if not info.get('is_live'):
            return None
        await self.voice.join_video(chat_id, info['url'])
        info['type'] = 'live'
        self.current[chat_id] = info
        return info

    async def force_play(self, chat_id: int, query: str, user_id: int=0, video: bool=False):
        self.queues[chat_id] = []
        self.current[chat_id] = None
        await self.voice.leave_call(chat_id)
        return await self.play_song(chat_id, query, user_id, video)

    async def _play_next(self, chat_id: int):
        if chat_id not in self.queues or not self.queues[chat_id]:
            self.current[chat_id] = None
            return None
        if self.loop.get(chat_id) and self.current.get(chat_id):
            self.queues[chat_id].insert(0, self.current[chat_id])
        song = self.queues[chat_id].pop(0)
        self.current[chat_id] = song
        file_path = await self._download(song['url'])
        if not file_path:
            return await self._play_next(chat_id)
        is_video = song.get('type') == 'video' or song.get('is_live')
        if self.voice.is_active(chat_id):
            await self.voice.change_stream(chat_id, file_path, is_video)
        else:
            if is_video:
                await self.voice.join_video(chat_id, file_path)
            else:
                await self.voice.join_audio(chat_id, file_path)
        return song

    async def _download(self, url: str) -> Optional[str]:
        try:
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'cache/%(id)s.%(ext)s',
                'quiet': True, 'no_warnings': True,
            }
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                fp = ydl.prepare_filename(info)
                base = os.path.splitext(fp)[0]
                for ext in ['m4a','webm','opus','mp3']:
                    p = f"{base}.{ext}"
                    if os.path.exists(p): return p
                if os.path.exists(fp): return fp
            return None
        except Exception as e:
            self.log.error(f"Download error: {e}")
            return None

    async def skip(self, chat_id: int):
        return await self._play_next(chat_id)

    async def stop(self, chat_id: int):
        self.queues[chat_id] = []
        self.current[chat_id] = None
        await self.db.remove_active_call(chat_id)
        return await self.voice.leave_call(chat_id)

    def get_queue(self, chat_id: int):
        return self.queues.get(chat_id, [])

    def get_current(self, chat_id: int):
        return self.current.get(chat_id)

    async def shuffle(self, chat_id: int):
        if chat_id in self.queues and self.queues[chat_id]:
            random.shuffle(self.queues[chat_id])

    def set_loop(self, chat_id: int, enabled: bool):
        self.loop[chat_id] = enabled

    async def set_volume(self, chat_id: int, vol: int):
        self.volumes[chat_id] = max(0, min(200, vol))
        await self.db.set_chat_settings(chat_id, {"volume": self.volumes[chat_id]})

    async def pause(self, chat_id: int):
        return await self.voice.pause(chat_id)

    async def resume(self, chat_id: int):
        return await self.voice.resume(chat_id)

    def get_volume(self, chat_id: int):
        return self.volumes.get(chat_id, Config.DEFAULT_VOLUME)
