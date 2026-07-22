from pyrogram import Client, filters, enums
from pyrogram.types import Message

@Client.on_message(filters.command("warn") & filters.group)
async def warn_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to warn them.")
    target = message.reply_to_message.from_user
    uid = target.id
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason"
    db = client.bot_instance.db
    total = await db.warn_user(message.chat.id, uid, reason, message.from_user.id)
    await message.reply(
        f"⚠️ <b>Warned!</b>\n\n"
        f"User: {target.mention}\n"
        f"Reason: {reason}\n"
        f"Warns: <b>{total}/3</b>\n\n"
        f"{'🚫 User banned for 3 warns!' if total >= 3 else ''}"
    )
    if total >= 3:
        try:
            await message.chat.ban_member(uid)
            await db.remove_warns(message.chat.id, uid)
            await message.reply(f"🚫 {target.first_name} banned for 3 warns!")
        except Exception as e:
            await message.reply(f"❌ Could not ban: {e}")

@Client.on_message(filters.command(["unwarn","delwarn"]) & filters.group)
async def unwarn_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to remove warns.")
    target = message.reply_to_message.from_user
    await client.bot_instance.db.remove_warns(message.chat.id, target.id)
    await message.reply(f"✅ Warns cleared for {target.mention}")

@Client.on_message(filters.command(["warnings","warns"]))
async def warns_cmd(client: Client, message: Message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    warns = await client.bot_instance.db.get_warns(message.chat.id, target.id)
    if warns:
        text = f"⚠️ <b>Warnings for {target.first_name}</b>\n\n"
        for i, w in enumerate(warns, 1):
            text += f"{i}. {w['reason']} (by {w['admin']})\n"
        await message.reply(text)
    else:
        await message.reply(f"✅ {target.first_name} has no warnings.")
