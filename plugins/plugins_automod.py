import re
from pyrogram import Client, filters, enums
from pyrogram.types import Message

BAD_WORDS_LIST = ["fuck","shit","ass","bitch","damn","bastard","dick","porn","sex","xxx","nude","naked"]

@Client.on_message(filters.group & filters.text, group=2)
async def auto_mod(client: Client, message: Message):
    settings = await client.bot_instance.db.get_chat_settings(message.chat.id)
    if not settings.get("anti_spam", False): return
    uid = message.from_user.id
    text = message.text
    is_admin = False
    try:
        member = await message.chat.get_member(uid)
        if member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            is_admin = True
    except: pass
    if is_admin: return

    # Bad words filter
    bad_words = settings.get("bad_words", BAD_WORDS_LIST)
    for word in bad_words:
        if word.lower() in text.lower().split():
            await message.delete()
            warn_c = await client.bot_instance.db.warn_user(message.chat.id, uid, f"Bad word: {word}", client.bot_instance.bot.me.id)
            await message.reply(f"⚠️ {message.from_user.mention} No bad words! Warn {warn_c}/3")
            if warn_c >= 3:
                await message.chat.ban_member(uid)
                await message.reply(f"🚫 Banned for 3 warns!")
            return

    # Caps filter
    caps_limit = settings.get("caps_limit", 70)
    if len(text) > 10:
        caps = sum(1 for c in text if c.isupper())
        if caps / len(text) * 100 > caps_limit:
            await message.delete()
            await message.reply(f"🔇 {message.from_user.mention} Too many caps! Please type normally.")
            return

    # Spam filter (same message repeated)
    if hasattr(client, '_last_msg'):
        lm = client._last_msg.get(message.chat.id, {}).get(uid, {})
        if lm.get("text") == text:
            count = lm.get("count", 0) + 1
            if count >= 4:
                await message.delete()
                await message.reply(f"🚫 {message.from_user.mention} Stop spamming!")
                return
            client._last_msg[message.chat.id][uid] = {"text": text, "count": count}
        else:
            if message.chat.id not in client._last_msg: client._last_msg[message.chat.id] = {}
            client._last_msg[message.chat.id][uid] = {"text": text, "count": 1}
    else:
        client._last_msg = {message.chat.id: {uid: {"text": text, "count": 1}}}

@Client.on_message(filters.command(["antispam","setantispam"]) & filters.group)
async def set_antispam(client: Client, message: Message):
    settings = await client.bot_instance.db.get_chat_settings(message.chat.id)
    if len(message.command) > 1:
        val = message.command[1].lower()
        if val in ["on","true","yes"]:
            settings["anti_spam"] = True
            await client.bot_instance.db.set_chat_settings(message.chat.id, {"anti_spam": True})
            await message.reply("✅ Anti-spam enabled!")
        elif val in ["off","false","no"]:
            settings["anti_spam"] = False
            await client.bot_instance.db.set_chat_settings(message.chat.id, {"anti_spam": False})
            await message.reply("✅ Anti-spam disabled!")
        else:
            await message.reply("Usage: /antispam on/off")
    else:
        status = "ON" if settings.get("anti_spam") else "OFF"
        await message.reply(f"🛡️ <b>Auto-Mod</b>\n\nAnti-Spam: {status}\nCaps Limit: {settings.get('caps_limit', 70)}%\nBad Words: {len(settings.get('bad_words', []))}")

@Client.on_message(filters.command(["addbadword","addword"]) & filters.group)
async def add_badword(client: Client, message: Message):
    if len(message.command) < 2: return await message.reply("Usage: /addbadword <word>")
    word = message.command[1].lower()
    settings = await client.bot_instance.db.get_chat_settings(message.chat.id)
    words = settings.get("bad_words", [])
    if word not in words:
        words.append(word)
        await client.bot_instance.db.set_chat_settings(message.chat.id, {"bad_words": words})
        await message.reply(f"✅ Added <b>{word}</b> to bad words list!")
    else:
        await message.reply("Already in list!")

@Client.on_message(filters.command(["delbadword","removeword"]) & filters.group)
async def del_badword(client: Client, message: Message):
    if len(message.command) < 2: return await message.reply("Usage: /delbadword <word>")
    word = message.command[1].lower()
    settings = await client.bot_instance.db.get_chat_settings(message.chat.id)
    words = settings.get("bad_words", [])
    if word in words:
        words.remove(word)
        await client.bot_instance.db.set_chat_settings(message.chat.id, {"bad_words": words})
        await message.reply(f"✅ Removed <b>{word}</b> from bad words list!")
    else:
        await message.reply("Not in list!")

@Client.on_message(filters.command(["setcapslimit","capslimit"]) & filters.group)
async def set_caps(client: Client, message: Message):
    if len(message.command) < 2: return await message.reply("Usage: /setcapslimit <50-100>")
    try: limit = max(50, min(100, int(message.command[1])))
    except: return await message.reply("Invalid number!")
    await client.bot_instance.db.set_chat_settings(message.chat.id, {"caps_limit": limit})
    await message.reply(f"✅ Caps limit set to {limit}%")
