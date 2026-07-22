import asyncio, sys, os
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from config import Config
from database.mongo import MongoDB
from music.player import MusicPlayer
from music.calls import VoiceHandler
from games.engine import GameEngine
from utils.logger import Logger
from utils.helpers import Helpers

_orig_reply = Message.reply
_orig_reply_photo = Message.reply_photo
_orig_reply_audio = Message.reply_audio
_orig_reply_video = Message.reply_video
_orig_reply_animation = Message.reply_animation
_orig_reply_sticker = Message.reply_sticker
_orig_reply_dice = Message.reply_dice
_orig_edit = Message.edit

async def _sc_reply(self, text, **kwargs):
    if text and isinstance(text, str):
        text = Helpers.format_msg(text)
    return await _orig_reply(self, text, **kwargs)

async def _sc_reply_photo(self, photo, caption=None, **kwargs):
    if caption and isinstance(caption, str):
        caption = Helpers.format_msg(caption)
    return await _orig_reply_photo(self, photo, caption=caption, **kwargs)

async def _sc_reply_audio(self, audio, caption=None, **kwargs):
    if caption and isinstance(caption, str):
        caption = Helpers.format_msg(caption)
    return await _orig_reply_audio(self, audio, caption=caption, **kwargs)

async def _sc_reply_video(self, video, caption=None, **kwargs):
    if caption and isinstance(caption, str):
        caption = Helpers.format_msg(caption)
    return await _orig_reply_video(self, video, caption=caption, **kwargs)

async def _sc_reply_animation(self, animation, caption=None, **kwargs):
    if caption and isinstance(caption, str):
        caption = Helpers.format_msg(caption)
    return await _orig_reply_animation(self, animation, caption=caption, **kwargs)

async def _sc_reply_sticker(self, sticker, **kwargs):
    return await _orig_reply_sticker(self, sticker, **kwargs)

async def _sc_reply_dice(self, **kwargs):
    return await _orig_reply_dice(self, **kwargs)

async def _sc_edit(self, text, **kwargs):
    if text and isinstance(text, str):
        text = Helpers.format_msg(text)
    return await _orig_edit(self, text, **kwargs)

Message.reply = _sc_reply
Message.reply_photo = _sc_reply_photo
Message.reply_audio = _sc_reply_audio
Message.reply_video = _sc_reply_video
Message.reply_animation = _sc_reply_animation
Message.reply_sticker = _sc_reply_sticker
Message.reply_dice = _sc_reply_dice
Message.edit = _sc_edit

os.makedirs("cache", exist_ok=True)
os.makedirs("logs", exist_ok=True)

class ZeniiXMusic:
    def __init__(self):
        self.bot = None
        self.user = None
        self.db = MongoDB()
        self.log = Logger()
        self.music_player = None
        self.voice_handler = None
        self.game_engine = None
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        self.log.info("Starting Zenii X Music...")
        self.bot = Client(
            "ZeniiBot", api_id=Config.API_ID, api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML,
            plugins=dict(root="plugins")
        )
        self.user = Client(
            "ZeniiUser", api_id=Config.API_ID, api_hash=Config.API_HASH,
            session_string=Config.STRING_SESSION, parse_mode=ParseMode.HTML
        )
        await self.db.connect()
        self.log.info("Database connected.")
        self.voice_handler = VoiceHandler(self.user)
        self.music_player = MusicPlayer(self.bot, self.voice_handler, self.db)
        self.game_engine = GameEngine(self.bot, self.db)
        self.bot.bot_instance = self
        self.user.bot_instance = self
        await self.bot.start()
        await self.user.start()
        await self.voice_handler.start()
        self.scheduler.add_job(self._lottery_draw, "cron", hour=0, minute=0)
        self.scheduler.start()
        self.log.info(f"{Config.BOT_NAME} v{Config.VERSION} started!")
        if Config.LOG_GROUP_ID:
            try:
                await self.bot.send_message(Config.LOG_GROUP_ID,
                    Helpers.format_msg(f"🚀 <b>{Config.BOT_NAME}</b> v{Config.VERSION} started!"))
            except: pass
        await idle()
        await self.stop()

    async def _lottery_draw(self):
        try:
            from plugins.economy_ext import lottery_draw
            await lottery_draw(self.bot)
        except Exception as e:
            self.log.error(f"Lottery draw error: {e}")

    async def stop(self):
        self.scheduler.shutdown()
        await self.bot.stop()
        await self.user.stop()
        await self.db.close()
        self.log.info("Bot stopped.")

if __name__ == "__main__":
    bot = ZeniiXMusic()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        pass
