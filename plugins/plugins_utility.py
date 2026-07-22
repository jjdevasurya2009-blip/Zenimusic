from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.buttons import Buttons

@Client.on_message(filters.command("lyrics"))
async def lyrics_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /lyrics <song>")
    query = message.text.split(None, 1)[1]
    msg = await message.reply(f"🔍 Searching lyrics...")
    try:
        import requests
        url = f"https://api.lyrics.ovh/v1/{query.replace(' ', '%20')}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            lyrics = resp.json().get("lyrics", "Not found")
            if len(lyrics) > 4000: lyrics = lyrics[:4000] + "..."
            await msg.edit(f"📝 <b>Lyrics:</b> {query}\n\n<code>{lyrics}</code>")
        else:
            await msg.edit("❌ Lyrics not found.")
    except:
        await msg.edit("❌ Could not fetch lyrics.")

@Client.on_message(filters.command("search"))
async def search_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /search <query>")
    query = message.text.split(None, 1)[1]
    msg = await message.reply(f"🔍 Searching: {query}")
    try:
        from yt_dlp import YoutubeDL
        with YoutubeDL({"quiet":True,"no_warnings":True,"extract_flat":True}) as ydl:
            results = ydl.extract_info(f"ytsearch5:{query}", download=False)
            if 'entries' in results:
                text = f"🔍 <b>Results:</b> {query}\n\n"
                for i, e in enumerate(results['entries'], 1):
                    d = e.get('duration',0)
                    text += f"{i}. <b>{e['title']}</b> ({d//60}:{d%60:02d})\n   👤 {e.get('uploader','?')}\n\n"
                await msg.edit(text)
            else:
                await msg.edit("No results.")
    except Exception as e:
        await msg.edit(f"❌ {e}")

@Client.on_message(filters.command(["song","video","download"]))
async def dl_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /song <name> or /video <name>")
    query = message.text.split(None, 1)[1]
    is_video = message.command[0] == "video"
    msg = await message.reply("📥 Downloading...")
    try:
        from yt_dlp import YoutubeDL
        opts = {
            'format': 'bestvideo+bestaudio/best' if is_video else 'bestaudio/best',
            'quiet': True, 'no_warnings': True,
            'outtmpl': f'cache/%(title)s.{"mp4" if is_video else "mp3"}',
        }
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if 'entries' in info and info['entries']: info = info['entries'][0]
            ydl.download([info['webpage_url']])
            import os
            fp = ydl.prepare_filename(info)
            base = os.path.splitext(fp)[0]
            ext = '.mp4' if is_video else '.mp3'
            fpath = base + ext
            if os.path.exists(fpath):
                if is_video:
                    await message.reply_video(fpath, caption=f"📥 {info['title']}")
                else:
                    await message.reply_audio(fpath, caption=f"📥 {info['title']}",
                        performer=info.get('uploader',''), title=info['title'])
                await msg.delete()
                os.remove(fpath)
    except Exception as e:
        await msg.edit(f"❌ {e}")

@Client.on_message(filters.command(["settings","config"]))
async def settings_cmd(client: Client, message: Message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        settings = await client.bot_instance.db.get_chat_settings(message.chat.id)
        text = "⚙️ <b>Chat Settings</b>\n\n"
        text += f"Volume: {settings.get('volume',100)}%\n"
        text += f"Loop: {'ON' if settings.get('loop') else 'OFF'}\n"
        text += f"Auto Play: {'ON' if settings.get('autoplay') else 'OFF'}\n"
        text += f"Auto Leave: {'ON' if settings.get('autoleave') else 'OFF'}\n"
        text += f"Night Mode: {'ON' if settings.get('nightmode') else 'OFF'}\n"
        text += f"Queue Limit: {settings.get('limit',20)}"
        await message.reply(text, reply_markup=Buttons.settings_buttons())
    else:
        await message.reply("Use this in a group!")

@Client.on_message(filters.command("hack"))
async def hack_cmd(client: Client, message: Message):
    import asyncio
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else message.from_user.first_name
    msg = await message.reply(f"🎭 Hacking {target}...")
    stages = [
        "🔍 Finding IP...", "📡 Bypassing firewall...",
        "🔓 Cracking passwords...", "📁 Downloading data...",
        "🗑 Clearing traces...", "✅ HACKED! Just pranking! 😄"
    ]
    for s in stages:
        await asyncio.sleep(1.2); await msg.edit(s)
