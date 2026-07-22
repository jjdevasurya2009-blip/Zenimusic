from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from utils.buttons import Buttons
from utils.helpers import Helpers

h = Helpers()

def is_owner(uid):
    return uid == Config.OWNER_ID

async def is_owner_or_co(db, uid):
    return uid == Config.OWNER_ID or await db.is_co_owner(uid)

@Client.on_message(filters.command("admin") & filters.private)
async def admin_panel(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    await message.react("⚙️")
    text = (
        "⚙️ <b>Admin Panel</b>\n\n"
        "Manage bot settings, users, and more.\n"
        f"Active calls: {client.bot_instance.voice_handler.call_count}"
    )
    await message.reply(text, reply_markup=Buttons.admin_panel())

@Client.on_message(filters.command(["stats","status"]))
async def stats_cmd(client: Client, message: Message):
    if not await is_owner_or_co(client.bot_instance.db, message.from_user.id):
        return await message.reply("❌ No permission.")
    stats = await client.bot_instance.db.get_bot_stats()
    calls = client.bot_instance.voice_handler.call_count
    text = (
        "📊 <b>Bot Statistics</b>\n\n"
        f"👥 Users: <b>{stats['users']}</b>\n"
        f"👥 Groups: <b>{stats['groups']}</b>\n"
        f"📞 Active Calls: <b>{calls}</b>\n"
        f"⚡ Version: {Config.VERSION}\n"
        f"🤖 Owner: {Config.OWNER_ID}"
    )
    await message.reply(text)

@Client.on_message(filters.command(["ac","activecalls"]))
async def ac_cmd(client: Client, message: Message):
    count = client.bot_instance.voice_handler.call_count
    await message.react("📞")
    await message.reply(f"📞 <b>Active Voice Calls:</b> {count}")

@Client.on_message(filters.command(["ping","alive"]))
async def ping_cmd(client: Client, message: Message):
    import time
    start = time.time()
    msg = await message.reply("🏓 Pong!")
    end = time.time()
    await msg.edit(f"🏓 <b>Pong!</b>\n⚡ {round((end-start)*1000)}ms")

@Client.on_message(filters.command("id"))
async def id_cmd(client: Client, message: Message):
    text = f"📌 <b>IDs</b>\nChat: <code>{message.chat.id}</code>\nUser: <code>{message.from_user.id}</code>"
    if message.reply_to_message:
        text += f"\nReplied: <code>{message.reply_to_message.from_user.id}</code>"
    await message.reply(text)

@Client.on_message(filters.command(["broadcast","announce"]))
async def broadcast_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply("Usage: /broadcast <message>")
    text = message.text.split(None, 1)[1]
    await message.reply(f"📢 Broadcasting...")
    users = await client.bot_instance.db.db.users.find({"banned": False}).to_list(length=None)
    sent = 0
    for u in users:
        try:
            await client.send_message(u["user_id"], Helpers.format_msg(f"📢 <b>Broadcast</b>\n\n{text}"))
            sent += 1
        except:
            pass
    await message.reply(f"✅ Sent to {sent}/{len(users)} users.")

@Client.on_message(filters.command("premium") & filters.private)
async def premium_manage(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return
    parts = message.command
    if len(parts) < 3:
        return await message.reply("Usage: /premium <add|remove|list> [user_id] [days]")
    action = parts[1]
    db = client.bot_instance.db
    if action == "add":
        uid = int(parts[2])
        days = int(parts[3]) if len(parts) > 3 else 30
        await db.set_premium(uid, days)
        await message.reply(f"⭐ Premium added to {uid} for {days} days!")
        try: await client.send_message(uid, Helpers.format_msg("🎉 <b>Premium Activated!</b>\n\nYou now have premium features!"))
        except: pass
    elif action == "remove":
        uid = int(parts[2])
        await db.remove_premium(uid)
        await message.reply(f"⭐ Premium removed from {uid}")
    elif action == "list":
        users = await db.db.users.find({"is_premium": True}).to_list(length=None)
        text = "⭐ <b>Premium Users</b>\n\n"
        for u in users:
            expiry = u.get("premium_expiry", "N/A")
            text += f"• {u.get('name','?')} ({u['user_id']}) - Exp: {expiry}\n"
        await message.reply(text or "No premium users.")

@Client.on_message(filters.command("eval") & filters.private)
async def eval_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id): return
    if len(message.command) < 2: return
    code = message.text.split(None, 1)[1]
    try:
        result = eval(code)
        await message.reply(f"<code>{result}</code>")
    except Exception as e:
        await message.reply(f"❌ {e}")

@Client.on_message(filters.command(["ban","unban","mute","unmute"]) & filters.group)
async def mod_cmds(client: Client, message: Message):
    cmd = message.command[0]
    if not message.reply_to_message:
        return await message.reply(f"Reply to a user to {cmd} them.")
    target = message.reply_to_message.from_user
    try:
        if cmd == "ban":
            await message.chat.ban_member(target.id)
            await message.reply(f"🚫 Banned {target.first_name}")
        elif cmd == "unban":
            await message.chat.unban_member(target.id)
            await message.reply(f"✅ Unbanned {target.first_name}")
        elif cmd == "mute":
            from pyrogram.types import ChatPermissions
            await message.chat.restrict_member(target.id, ChatPermissions(can_send_messages=False))
            await message.reply(f"🔇 Muted {target.first_name}")
        elif cmd == "unmute":
            from pyrogram.types import ChatPermissions
            await message.chat.restrict_member(target.id, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
            await message.reply(f"🔊 Unmuted {target.first_name}")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@Client.on_message(filters.command(["pin","purge"]) & filters.group)
async def group_manage(client: Client, message: Message):
    cmd = message.command[0]
    if cmd == "pin" and message.reply_to_message:
        await message.reply_to_message.pin()
        await message.reply("📌 Pinned!")
    elif cmd == "purge":
        try: count = int(message.command[1]) if len(message.command)>1 else 10
        except: count = 10
        count = min(100, max(1, count))
        deleted = 0
        async for msg in message.chat.get_history(limit=count):
            try: await msg.delete(); deleted += 1
            except: pass
        await message.reply(f"🗑 Deleted {deleted} messages.")
