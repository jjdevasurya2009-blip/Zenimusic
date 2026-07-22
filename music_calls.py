import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import InputAudioStream, InputVideoStream, InputStream
from typing import Optional, Dict, Callable

class VoiceHandler:
    def __init__(self, user_client: Client):
        self.user = user_client
        self.pytgcalls = PyTgCalls(user_client)
        self.active_calls: Dict[int, dict] = {}
        self.end_callbacks: Dict[int, Callable] = {}
        self.playing_type: Dict[int, str] = {}  # audio, video, radio, live

    async def start(self):
        await self.pytgcalls.start()

    async def join_audio(self, chat_id: int, file_path: str):
        try:
            await self.pytgcalls.join_group_call(
                chat_id,
                InputStream(InputAudioStream(file_path))
            )
            self.active_calls[chat_id] = {"type": "audio", "path": file_path}
            self.playing_type[chat_id] = "audio"
            return True
        except Exception as e:
            return False

    async def join_video(self, chat_id: int, file_path: str):
        try:
            await self.pytgcalls.join_group_call(
                chat_id,
                InputStream(
                    InputVideoStream(file_path),
                    InputAudioStream(file_path)
                )
            )
            self.active_calls[chat_id] = {"type": "video", "path": file_path}
            self.playing_type[chat_id] = "video"
            return True
        except Exception as e:
            return False

    async def join_radio(self, chat_id: int, stream_url: str):
        try:
            await self.pytgcalls.join_group_call(
                chat_id,
                InputStream(InputAudioStream(stream_url))
            )
            self.active_calls[chat_id] = {"type": "radio", "path": stream_url}
            self.playing_type[chat_id] = "radio"
            return True
        except Exception as e:
            return False

    async def change_stream(self, chat_id: int, file_path: str, is_video: bool = False):
        try:
            if is_video:
                await self.pytgcalls.change_stream(
                    chat_id,
                    InputStream(
                        InputVideoStream(file_path),
                        InputAudioStream(file_path)
                    )
                )
            else:
                await self.pytgcalls.change_stream(
                    chat_id,
                    InputStream(InputAudioStream(file_path))
                )
            return True
        except:
            return False

    async def leave_call(self, chat_id: int):
        try:
            await self.pytgcalls.leave_group_call(chat_id)
            self.active_calls.pop(chat_id, None)
            self.playing_type.pop(chat_id, None)
            return True
        except:
            return False

    async def pause(self, chat_id: int):
        try:
            await self.pytgcalls.pause_stream(chat_id)
            return True
        except: return False

    async def resume(self, chat_id: int):
        try:
            await self.pytgcalls.resume_stream(chat_id)
            return True
        except: return False

    async def mute(self, chat_id: int):
        try: await self.pytgcalls.mute_stream(chat_id); return True
        except: return False

    async def unmute(self, chat_id: int):
        try: await self.pytgcalls.unmute_stream(chat_id); return True
        except: return False

    def set_end_callback(self, chat_id: int, cb: Callable):
        self.end_callbacks[chat_id] = cb

    @property
    def call_count(self):
        return len(self.active_calls)

    def is_active(self, chat_id: int) -> bool:
        return chat_id in self.active_calls
