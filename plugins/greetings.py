from pyrogram import Client, filters, enums
from pyrogram.types import Message

@Client.on_message(filters.new_chat_members, group=1)
async def welcome_member(client: Client, message: Message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id: return
        settings = await client.bot_instance.db.get_chat_settings(message.chat.id)
        if not settings.get("welcome", True): return
        msg = settings.get("welcome_msg", "")
        if msg:
            text = msg.replace("{name}", member.first_name).replace("{mention}", member.mention).replace("{title}", message.chat.title)
            await message.reply(text)
        else:
            await message.reply(f"👋 Welcome {member.mention} to {message.chat.title}!")

@Client.on_message(filters.left_chat_member, group=1)
async def goodbye_member(client: Client, message: Message):
    user = message.left_chat_member
    if user.id == (await client.get_me()).id: return
    settings = await client.bot_instance.db.get_chat_settings(message.chat.id)
    if not settings.get("welcome", True): return
    msg = settings.get("goodbye_msg", "")
    if msg:
        text = msg.replace("{name}", user.first_name).replace("{mention}", user.mention).replace("{title}", message.chat.title)
        await message.reply(text)

@Client.on_message(filters.command(["setwelcome","setgreeting"]) & filters.group)
async def set_welcome_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /setwelcome <message>\nUse {name}, {mention}, {title} as placeholders.\n/setwelcome default to reset")
    text = message.text.split(None, 1)[1]
    if text.lower() == "default":
        await client.bot_instance.db.set_chat_settings(message.chat.id, {"welcome_msg": ""})
        await message.reply("✅ Welcome message reset to default!")
    else:
        await client.bot_instance.db.set_chat_settings(message.chat.id, {"welcome_msg": text})
        await message.reply(f"✅ Welcome message set!\n\nPreview: {text.replace('{name}',message.from_user.first_name).replace('{mention}',message.from_user.mention).replace('{title}',message.chat.title)}")

@Client.on_message(filters.command(["setgoodbye","setbye"]) & filters.group)
async def set_goodbye_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /setgoodbye <message>\nUse {name}, {mention}, {title} as placeholders.\n/setgoodbye default to reset")
    text = message.text.split(None, 1)[1]
    if text.lower() == "default":
        await client.bot_instance.db.set_chat_settings(message.chat.id, {"goodbye_msg": ""})
        await message.reply("✅ Goodbye message reset to default!")
    else:
        await client.bot_instance.db.set_chat_settings(message.chat.id, {"goodbye_msg": text})
        await message.reply(f"✅ Goodbye message set!")

@Client.on_message(filters.command(["welcome","greeting"]) & filters.group)
async def welcome_status(client: Client, message: Message):
    settings = await client.bot_instance.db.get_chat_settings(message.chat.id)
    status = "ON" if settings.get("welcome", True) else "OFF"
    w_msg = settings.get("welcome_msg", "Default") or "Default"
    g_msg = settings.get("goodbye_msg", "Default") or "Default"
    await message.reply(
        f"👋 <b>Greetings Settings</b>\n\n"
        f"Status: {status}\n"
        f"Welcome: {w_msg[:50]}\n"
        f"Goodbye: {g_msg[:50]}\n\n"
        f"Use /setwelcome <msg> and /setgoodbye <msg> to customize!"
    )
