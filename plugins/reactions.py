from pyrogram import Client, filters, enums
from pyrogram.types import Message
import re, random

REACTION_EMOJIS = ["👍","❤️","🔥","🎵","🎶","✨","💫","👌","🎯","💯","🥳","🎉","🌟","⚡","💎","🎸","🎹","🎺","🎷","🎤","🎧","📻","🎼","🎵"]
CMD_PATTERN = re.compile(r'^/\w+')

@Client.on_message(filters.group & filters.text & ~filters.service)
async def auto_react_group(client: Client, message: Message):
    text = message.text
    if CMD_PATTERN.match(text):
        emoji = random.choice(REACTION_EMOJIS)
        try: await message.react(emoji=emoji)
        except: pass

@Client.on_message(filters.private & ~filters.command([]))
async def auto_react_pm(client: Client, message: Message):
    if message.text and not message.text.startswith("/"):
        try:
            await message.react(emoji=random.choice(["👍","❤️","🔥","💫","✨"]))
        except: pass

@Client.on_message(filters.new_chat_members)
async def welcome_react(client: Client, message: Message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            await message.react(emoji="🎉")
            settings = await client.bot_instance.db.get_chat_settings(message.chat.id)
            if settings.get("welcome", True):
                await message.reply(
                    "🎵 <b>ZENII X MUSIC</b> joined!\n\n"
                    "• /play <song> - Play music\n"
                    "• /game - Play games\n"
                    "• /help - All commands\n\n"
                    "Start a voice chat and enjoy! 🎶"
                )
            await client.bot_instance.db.add_log("group_add", {"chat_id": message.chat.id, "title": message.chat.title})
