import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from utils.buttons import Buttons

@Client.on_message(filters.command("playlist"))
async def playlist_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    await client.bot_instance.db.register_user(uid, message.from_user.first_name)
    parts = message.command
    if len(parts) < 2:
        playlists = await db.get_playlist(uid)
        if not playlists:
            return await message.reply(
                "📋 <b>Playlists</b>\n\nYou have no playlists.\n"
                "Usage:\n"
                "/playlist create <name> - Create playlist\n"
                "/playlist add <name> <song> - Add song\n"
                "/playlist remove <name> <index> - Remove song\n"
                "/playlist delete <name> - Delete playlist\n"
                "/playlist view <name> - View playlist\n"
                "/playlist list - List all\n"
                "/playlist limit - Your limit"
            )
        text = "📋 <b>Your Playlists</b>\n\n"
        for name, songs in playlists.items():
            text += f"• <b>{name}</b> ({len(songs)} songs)\n"
        await message.reply(text)
        return
    action = parts[1]
    if action == "create" and len(parts) > 2:
        name = parts[2]
        playlists = await db.get_playlist(uid)
        limit = await db.get_playlist_limit(uid)
        if len(playlists) >= limit:
            return await message.reply(f"❌ Playlist limit ({limit}) reached. Premium users get higher!")
        if name in playlists:
            return await message.reply("❌ Playlist already exists.")
        playlists[name] = []
        await db.save_playlist(uid, playlists)
        await message.reply(f"✅ Playlist '{name}' created!")
    elif action == "delete" and len(parts) > 2:
        name = parts[2]
        playlists = await db.get_playlist(uid)
        if name in playlists:
            del playlists[name]
            await db.save_playlist(uid, playlists)
            await message.reply(f"✅ Playlist '{name}' deleted.")
        else:
            await message.reply("❌ Playlist not found.")
    elif action == "view" and len(parts) > 2:
        name = parts[2]
        playlists = await db.get_playlist(uid)
        if name in playlists:
            songs = playlists[name]
            text = f"📋 <b>{name}</b> ({len(songs)} songs)\n\n"
            for i, s in enumerate(songs, 1):
                text += f"{i}. {s[:50]}\n"
            await message.reply(text, reply_markup=Buttons.back_button("help"))
        else:
            await message.reply("❌ Playlist not found.")
    elif action == "add" and len(parts) > 3:
        name = parts[2]
        song = " ".join(parts[3:])
        playlists = await db.get_playlist(uid)
        if name in playlists:
            limit = await db.get_playlist_limit(uid)
            if len(playlists[name]) >= limit:
                return await message.reply(f"❌ Song limit ({limit}) for this playlist.")
            playlists[name].append(song)
            await db.save_playlist(uid, playlists)
            await message.reply(f"✅ Added to '{name}': {song}")
        else:
            await message.reply("❌ Playlist not found.")
    elif action == "remove" and len(parts) > 3:
        name = parts[2]
        try: idx = int(parts[3]) - 1
        except: return await message.reply("Usage: /playlist remove <name> <index>")
        playlists = await db.get_playlist(uid)
        if name in playlists and 0 <= idx < len(playlists[name]):
            removed = playlists[name].pop(idx)
            await db.save_playlist(uid, playlists)
            await message.reply(f"✅ Removed: {removed}")
        else:
            await message.reply("❌ Invalid index or playlist.")
    elif action == "list":
        playlists = await db.get_playlist(uid)
        if not playlists:
            return await message.reply("No playlists.")
        text = "📋 <b>Playlists</b>\n\n"
        for name, songs in playlists.items():
            text += f"• {name} ({len(songs)} songs)\n"
        await message.reply(text)
    elif action == "limit":
        limit = await db.get_playlist_limit(uid)
        is_prem = await db.is_premium(uid)
        await message.reply(
            f"📋 <b>Playlist Limit</b>\n\n"
            f"Your limit: <b>{limit}</b> playlists\n"
            f"Premium: <b>{__import__('config').Config.PREMIUM_PLAYLIST_LIMIT}</b>\n"
            f"Status: {'⭐ Premium' if is_prem else 'Free'}"
        )
    else:
        await message.reply("❌ Unknown command. Use /playlist for help.")

@Client.on_message(filters.command("playfrom") & filters.group)
async def playfrom_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /playfrom <playlist_name>")
    name = message.command[1]
    uid = message.from_user.id
    playlists = await client.bot_instance.db.get_playlist(uid)
    if name in playlists:
        songs = playlists[name]
        if not songs:
            return await message.reply("❌ Playlist is empty.")
        msg = await message.reply(f"🎵 Playing playlist '{name}' ({len(songs)} songs)...")
        for song in songs:
            await client.bot_instance.music_player.play_song(message.chat.id, song, uid)
        await msg.edit(f"✅ Added {len(songs)} songs from '{name}' to queue!")
    else:
        await message.reply("❌ Playlist not found.")

@Client.on_message(filters.command(["importpl","importplaylist","import"]) & filters.private)
async def import_playlist_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /importpl <YouTube/Spotify playlist URL>")
    url = message.command[1]
    uid = message.from_user.id
    db = client.bot_instance.db
    msg = await message.reply("📥 Importing playlist...")
    try:
        from yt_dlp import YoutubeDL
        opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "ignoreerrors": True}
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info or 'entries' not in info:
            return await msg.edit("❌ Could not parse playlist. Make sure it's public!")
        entries = [e for e in info['entries'] if e]
        playlist_name = info.get('title', 'Imported')[:30]
        songs = []
        for e in entries:
            title = e.get('title', 'Unknown')
            url2 = e.get('webpage_url') or f"ytsearch:{title}"
            songs.append(url2)
        playlists = await db.get_playlist(uid)
        limit = await db.get_playlist_limit(uid)
        if len(playlists) >= limit:
            return await msg.edit(f"❌ Playlist limit ({limit}) reached. Delete some first!")
        if playlist_name in playlists:
            playlists[playlist_name].extend(songs[:50])
        else:
            playlists[playlist_name] = songs[:50]
        await db.save_playlist(uid, playlists)
        total = len(songs[:50])
        await msg.edit(f"✅ Imported <b>{total}</b> songs into playlist '<b>{playlist_name}</b>'!\nUse /playfrom {playlist_name} to play!")
    except Exception as e:
        await msg.edit(f"❌ Import failed: {e}")
