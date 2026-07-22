from pyrogram import Client, filters, enums
from pyrogram.types import Message

@Client.on_message(filters.command(["tagall","everyone","all"]))
async def tagall_cmd(client: Client, message: Message):
    if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply("❌ Groups only.")
    settings = await client.bot_instance.db.get_chat_settings(message.chat.id)
    if not settings.get("tagall", True):
        return await message.reply("❌ TagAll disabled by admin.")
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "Hey everyone!"
    msg = await message.reply(f"📢 <b>TagAll</b>\n\n{reason}\n\nGathering members...")
    mentions = []
    count = 0
    async for member in message.chat.get_members(limit=200):
        if not member.user.is_bot and not member.user.is_deleted:
            mentions.append(member.user.mention)
            count += 1
    chunks = [mentions[i:i+5] for i in range(0, len(mentions), 5)]
    text = f"📢 <b>TagAll</b> — {reason}\n\n"
    for chunk in chunks[:40]:
        text += " ".join(chunk) + "\n"
    if len(text) > 4000:
        text = text[:4000] + "..."
    await msg.edit(text)

@Client.on_message(filters.command(["tagadmins","adminlist"]))
async def tagadmins_cmd(client: Client, message: Message):
    if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return
    admins = []
    async for m in message.chat.get_members(filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if not m.user.is_bot:
            admins.append(m.user.mention)
    text = "👮 <b>Admins:</b>\n" + "\n".join(admins) if admins else "No admins found."
    await message.reply(text)
