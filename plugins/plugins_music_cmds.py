import asyncio
from pyrogram import Client, filters, emoji
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import Config
from utils.buttons import Buttons
from utils.helpers import Helpers
from utils.decorators import group_only, check_auth

h = Helpers()

@Client.on_message(filters.command("play") & filters.group)
@group_only
async def play_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /play <song name or URL>")
    query = message.text.split(None, 1)[1]
    uid = message.from_user.id
    await message.react(emoji=h.random_emoji())
    await client.bot_instance.db.inc_user(uid, "songs_played")
    em = h.playing_emojis()
    msg = await message.reply(f"{em} Processing your vibe...")
    bot = client.bot_instance
    result = await bot.music_player.play_song(message.chat.id, query, uid)
    if result is None:
        await msg.edit("❌ Could not find or play that song.")
    elif result == "queue_full":
        limit = await bot.db.get_queue_size(uid)
        await msg.edit(f"❌ Queue full ({limit} max). Premium users get higher limit!")
    else:
        s = bot.music_player.get_current(message.chat.id) or result
        dur = h.format_time(s['duration']) if s.get('duration') else "Live"
        await bot.db.add_active_call(message.chat.id)
        text = (
            f"{emoji.MUSICAL_NOTE} <b>Now Playing</b>\n\n"
            f"<b>Title:</b> {s['title']}\n"
            f"<b>Artist:</b> {s['artist']}\n"
            f"<b>Duration:</b> {dur}\n"
            f"<b>Requested:</b> {message.from_user.mention}"
        )
        await msg.delete()
        await message.reply_photo(s.get('thumbnail',''), caption=text,
                                   reply_markup=Buttons.music_controls())

@Client.on_message(filters.command("vplay") & filters.group)
@group_only
async def vplay_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /vplay <song or URL>")
    query = message.text.split(None, 1)[1]
    await message.react(emoji=h.random_emoji())
    msg = await message.reply("📺 Searching video...")
    bot = client.bot_instance
    result = await bot.music_player.play_song(message.chat.id, query, message.from_user.id, video=True)
    if result is None:
        await msg.edit("❌ Could not find video.")
    elif result == "queue_full":
        await msg.edit("❌ Queue full!")
    else:
        await msg.delete()
        await bot.db.add_active_call(message.chat.id)
        s = bot.music_player.get_current(message.chat.id) or result
        await message.reply_video(s.get('thumbnail',''),
            caption=f"📺 <b>Now Playing Video:</b> {s['title']}\n👤 {s['artist']}",
            reply_markup=Buttons.music_controls())

@Client.on_message(filters.command("radio") & filters.group)
@group_only
async def radio_cmd(client: Client, message: Message):
    bot = client.bot_instance
    if len(message.command) > 1:
        station = message.command[1].lower()
        result = await bot.music_player.play_radio(message.chat.id, station)
        if result:
            await message.react(emoji=h.random_emoji())
            await bot.db.add_active_call(message.chat.id)
            await message.reply(
                f"📻 <b>Radio: {station.title()}</b>\n\n"
                f"Streaming {station} radio!\n"
                f"Use /stop to stop.",
                reply_markup=Buttons.music_controls()
            )
        else:
            stations = "\n".join([f"• /radio {s}" for s in bot.music_player.radio_stations])
            await message.reply(f"❌ Station not found.\n\nAvailable:\n{stations}")
    else:
        stations = "\n".join([f"• /radio {s}" for s in bot.music_player.radio_stations])
        await message.reply(f"📻 <b>Radio Stations</b>\n\n{stations}")

@Client.on_message(filters.command("live") & filters.group)
@group_only
async def live_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /live <YouTube live URL>")
    url = message.command[1]
    msg = await message.reply("🔴 Connecting to live stream...")
    bot = client.bot_instance
    result = await bot.music_player.play_live(message.chat.id, url)
    if result:
        await msg.edit(
            f"🔴 <b>Live Streaming</b>\n\n"
            f"<b>{result['title']}</b>\n"
            f"👤 {result['artist']}",
            reply_markup=Buttons.music_controls()
        )
    else:
        await msg.edit("❌ Could not stream. Make sure it's a live YouTube URL.")

@Client.on_message(filters.command("forceplay") & filters.group)
@group_only
async def forceplay_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /forceplay <song>")
    if not await client.bot_instance.db.check_auth(message.from_user.id, "play"):
        return await message.reply("❌ You don't have permission for force play.")
    query = message.text.split(None, 1)[1]
    msg = await message.reply("⚡ Force playing...")
    bot = client.bot_instance
    result = await bot.music_player.force_play(message.chat.id, query, message.from_user.id)
    if result:
        await msg.edit(f"⚡ Force played: {result['title']}")
    else:
        await msg.edit("❌ Could not force play.")

@Client.on_message(filters.command(["pause","resume","skip","stop","shuffle","loop"]) & filters.group)
@group_only
async def control_cmds(client: Client, message: Message):
    cmd = message.command[0]
    bot = client.bot_instance
    mp = bot.music_player
    cid = message.chat.id
    responses = {
        "pause": ("⏸ Paused", lambda: mp.pause(cid)),
        "resume": ("▶️ Resumed", lambda: mp.resume(cid)),
        "skip": ("⏭ Skipped", lambda: mp.skip(cid)),
        "stop": (Helpers.interactive_leave(), lambda: mp.stop(cid)),
        "shuffle": ("🔀 Shuffled", lambda: mp.shuffle(cid)),
        "loop": ("🔁 Loop toggled", lambda: mp.set_loop(cid, not mp.loop.get(cid, False))),
    }
    if cmd in responses:
        text, action = responses[cmd]
        await action()
        await message.react(emoji=h.random_emoji())
        await message.reply(text)

@Client.on_message(filters.command("volume") & filters.group)
@group_only
async def volume_cmd(client: Client, message: Message):
    if len(message.command) > 1:
        try:
            vol = max(0, min(200, int(message.command[1])))
            await client.bot_instance.music_player.set_volume(message.chat.id, vol)
            await message.reply(f"🔊 Volume: {vol}%")
        except:
            await message.reply("Usage: /volume <1-200>")
    else:
        vol = client.bot_instance.music_player.get_volume(message.chat.id)
        await message.reply(f"🔊 Current volume: {vol}%")

@Client.on_message(filters.command("queue") & filters.group)
@group_only
async def queue_cmd(client: Client, message: Message):
    bot = client.bot_instance
    queue = bot.music_player.get_queue(message.chat.id)
    current = bot.music_player.get_current(message.chat.id)
    text = "📋 <b>Queue</b>\n\n"
    if current:
        text += f"▶️ <b>Now:</b> {current['title']}\n\n"
    if queue:
        for i, s in enumerate(queue[:15], 1):
            text += f"{i}. {s['title'][:40]}\n"
        if len(queue) > 15:
            text += f"\n+{len(queue)-15} more..."
    else:
        text += "Empty queue. Add songs with /play!"
    await message.react(emoji=emoji.CLIPBOARD)
    await message.reply(text, reply_markup=Buttons.queue_buttons(0,1,message.chat.id))

@Client.on_message(filters.command(["current","nowplaying"]) & filters.group)
@group_only
async def current_cmd(client: Client, message: Message):
    s = client.bot_instance.music_player.get_current(message.chat.id)
    if s:
        await message.reply(f"▶️ <b>Now Playing:</b> {s['title']}\n👤 {s['artist']}")
    else:
        await message.reply("❌ Nothing playing.")

@Client.on_message(filters.command("seek") & filters.group)
@group_only
async def seek_cmd(client: Client, message: Message):
    if len(message.command) > 1:
        await message.reply("⏩ Seek feature coming soon!")
    else:
        await message.reply("Usage: /seek <seconds> or mm:ss")

# ==================== VOTE SKIP ====================

_skip_votes = {}

@Client.on_message(filters.command(["voteskip","vskip","skipvote"]) & filters.group)
@group_only
async def voteskip_cmd(client: Client, message: Message):
    cid = message.chat.id
    mp = client.bot_instance.music_player
    current = mp.get_current(cid)
    if not current:
        return await message.reply("❌ Nothing is playing!")
    uid = message.from_user.id
    if uid not in _skip_votes:
        _skip_votes[uid] = set()
    voted = _skip_votes.get(cid, set())
    if uid in voted:
        return await message.reply("✅ You already voted to skip!")
    voted.add(uid)
    _skip_votes[cid] = voted
    try:
        members = []
        async for m in message.chat.get_members(limit=50):
            if not m.user.is_bot:
                members.append(m.user.id)
        total = max(1, len(members))
        needed = max(2, total // 2)
        have = len(voted)
        if have >= needed:
            await mp.skip(cid)
            _skip_votes[cid] = set()
            await message.reply(f"⏭ <b>Vote skip passed!</b> ({have}/{needed})\nSkipped {current['title'][:30]}")
        else:
            await message.reply(f"🗳️ <b>Vote Skip</b>\n\n{message.from_user.mention} wants to skip!\nVotes: {have}/{needed}\nCurrent: {current['title'][:30]}")
    except Exception as e:
        await message.reply(f"❌ Vote error: {e}")

@Client.on_message(filters.command(["forceskip","fs"]) & filters.group)
@group_only
async def forceskip_cmd(client: Client, message: Message):
    if not await client.bot_instance.db.check_auth(message.from_user.id, "skip"):
        return await message.reply("❌ You don't have skip permission!\nUse /voteskip instead.")
    await client.bot_instance.music_player.skip(message.chat.id)
    await message.reply("⏭ Force skipped!")

@Client.on_message(filters.command(["clearqueue","clearq"]) & filters.group)
@group_only
async def clear_queue_cmd(client: Client, message: Message):
    cid = message.chat.id
    mp = client.bot_instance.music_player
    mp.queues[cid] = []
    await message.reply("🗑️ Queue cleared!")

@Client.on_message(filters.command(["move","movequeue"]) & filters.group)
@group_only
async def move_queue_cmd(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply("Usage: /move <from> <to>\nMoves song in queue from position to position.")
    try: frm, to = int(message.command[1]) - 1, int(message.command[2]) - 1
    except: return await message.reply("Invalid positions!")
    mp = client.bot_instance.music_player
    q = mp.queues.get(message.chat.id, [])
    if 0 <= frm < len(q) and 0 <= to < len(q):
        song = q.pop(frm)
        q.insert(to, song)
        await message.reply(f"✅ Moved <b>{song['title'][:30]}</b> to position {to+1}")
    else:
        await message.reply("❌ Invalid positions. Use /queue to see numbers.")
