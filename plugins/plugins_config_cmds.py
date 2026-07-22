from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

def is_owner(uid):
    return uid == Config.OWNER_ID

@Client.on_message(filters.command("setcfg") & filters.private)
async def setcfg_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 3:
        return await message.reply("Usage: /setcfg <key> <value>")
    key = message.command[1]
    value = " ".join(message.command[2:])
    db = client.bot_instance.db
    cfg = await db.get_bot_config()
    cfg[key] = value
    await db.update_bot_config({key: value})
    await message.reply(f"✅ Updated {key} = {value}")

@Client.on_message(filters.command(["addco","addcoowner"]) & filters.private)
async def addco_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply("Usage: /addco <user_id>")
    uid = int(message.command[1])
    await client.bot_instance.db.add_co_owner(uid)
    await message.reply(f"✅ Added co-owner: {uid}")

@Client.on_message(filters.command(["removeco","removecoowner"]) & filters.private)
async def removeco_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply("Usage: /removeco <user_id>")
    uid = int(message.command[1])
    await client.bot_instance.db.remove_co_owner(uid)
    await message.reply(f"✅ Removed co-owner: {uid}")

@Client.on_message(filters.command(["addauth","authorize"]) & filters.private)
async def addauth_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply("Usage: /addauth <user_id>")
    uid = int(message.command[1])
    await client.bot_instance.db.add_auth_user(uid)
    await message.reply(f"✅ Authorized user: {uid}")

@Client.on_message(filters.command(["removeauth","deauthorize"]) & filters.private)
async def removeauth_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply("Usage: /removeauth <user_id>")
    uid = int(message.command[1])
    await client.bot_instance.db.remove_auth_user(uid)
    await message.reply(f"✅ Deauthorized: {uid}")

@Client.on_message(filters.command("setauth") & filters.private)
async def setauth_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 4:
        return await message.reply("Usage: /setauth <user_id> <command> <on/off>")
    uid = int(message.command[1])
    cmd = message.command[2]
    value = message.command[3].lower() == "on"
    au = await client.bot_instance.db.get_auth_user(uid)
    if au:
        perms = au.get("permissions", {})
        perms[cmd] = value
        await client.bot_instance.db.update_auth_perms(uid, perms)
        await message.reply(f"✅ Set /{cmd} to {'ON' if value else 'OFF'} for {uid}")
    else:
        await message.reply("❌ User not authorized. Use /addauth first.")

@Client.on_message(filters.command(["blacklist","bl"]) & filters.private)
async def blacklist_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply("Usage: /blacklist <chat_id>")
    cid = int(message.command[1])
    await client.bot_instance.db.blacklist_chat(cid)
    await message.reply(f"🚫 Blacklisted chat: {cid}")

@Client.on_message(filters.command(["whitelist","wl"]) & filters.private)
async def whitelist_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply("Usage: /whitelist <chat_id>")
    cid = int(message.command[1])
    await client.bot_instance.db.whitelist_chat(cid)
    await message.reply(f"✅ Whitelisted chat: {cid}")

@Client.on_message(filters.command(["setlimit","queuelimit"]) & filters.private)
async def setlimit_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply("Usage: /setlimit <number>")
    limit = max(5, min(100, int(message.command[1])))
    await client.bot_instance.db.update_bot_config({"max_queue": limit})
    await message.reply(f"✅ Queue limit set to {limit}")

@Client.on_message(filters.command(["setplaylistlimit","pllimit"]) & filters.private)
async def setpllimit_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    if len(message.command) < 3:
        return await message.reply("Usage: /setplaylistlimit <normal> <premium>")
    normal = int(message.command[1])
    premium = int(message.command[2])
    await client.bot_instance.db.update_bot_config({
        "playlist_limit": normal,
        "premium_playlist_limit": premium
    })
    await message.reply(f"✅ Normal: {normal}, Premium: {premium}")

@Client.on_message(filters.command(["maintenance","mode"]))
async def maintenance_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    db = client.bot_instance.db
    cfg = await db.get_bot_config()
    new_mode = not cfg.get("maintenance", False)
    await db.update_bot_config({"maintenance": new_mode})
    status = "ENABLED" if new_mode else "DISABLED"
    await message.reply(f"🔧 Maintenance mode: {status}")

@Client.on_message(filters.command(["logs","log"]))
async def view_logs(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("❌ Owner only.")
    logs = await client.bot_instance.db.get_logs(30)
    text = "📜 <b>Recent Logs</b>\n\n"
    for l in logs:
        t = l.get("type","?")
        d = str(l.get("data",{}))[:80]
        text += f"• [{t}] {d}\n"
    await message.reply(text[:4000])
