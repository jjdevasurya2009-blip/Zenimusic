from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command(["quote","q"]))
async def quote_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply(
            "<blockquote>Reply to a message to quote it!</blockquote>\n\n"
            "Example: Reply to someone and type /quote"
        )
    original = message.reply_to_message
    text = original.text or original.caption or ""
    if len(message.command) > 1:
        custom = message.text.split(None, 1)[1]
        text = custom
    if not text:
        return await message.reply("No text to quote!")
    name = original.from_user.first_name
    await message.reply(
        f"<blockquote>{text}</blockquote>\n"
        f"— <b>{name}</b>"
    )

@Client.on_message(filters.command(["quotereply","qr"]))
async def quote_reply_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to quote them!")
    original = message.reply_to_message
    text = original.text or original.caption or ""
    if len(message.command) > 1:
        add = message.text.split(None, 1)[1]
        text = text + "\n\n" + add if text else add
    if not text:
        return await message.reply("No text to quote!")
    name = original.from_user.first_name
    await original.reply(
        f"<blockquote>{text}</blockquote>\n"
        f"— <b>{name}</b>"
    )

@Client.on_message(filters.command(["quotemsg","qm"]))
async def quote_msg_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply(
            "<b>Usage:</b>\n"
            "/quote (reply) - Quote replied message\n"
            "/quotereply (reply) - Reply with quote\n"
            "/qm <text> - Create a quote from text\n\n"
            "Tip: You can also use <code>> text</code> at the start of any line for native quote formatting!"
        )
    text = message.text.split(None, 1)[1]
    if message.reply_to_message:
        name = message.reply_to_message.from_user.first_name
    else:
        name = message.from_user.first_name
    await message.reply(
        f"<blockquote>{text}</blockquote>\n"
        f"— <b>{name}</b>"
    )
