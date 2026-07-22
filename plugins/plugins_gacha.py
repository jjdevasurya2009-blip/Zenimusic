import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

CHARACTERS = {
    "5star": ["✨ Sailor Moon", "✨ Naruto", "✨ Goku", "✨ Luffy", "✨ Tanjiro", "✨ Levi", "✨ Gojo", "✨ Rem"],
    "4star": ["⭐ Pikachu", "⭐ Totoro", "⭐ Hello Kitty", "⭐ Hatsune Miku", "⭐ Doraemon", "⭐ Ash", "⭐ Izuku", "⭐ Eren"],
    "3star": ["🎴 Nezuko", "🎴 Zenitsu", "🎴 Inosuke", "🎴 Shinobu", "🎴 Kanao", "🎴 Genya", "🎴 Aoi", "🎴 Kiyoshi"],
}

@Client.on_message(filters.command(["wish","gacha","pull"]))
async def wish_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    cost = 500
    args = message.command
    multi = len(args) > 1 and args[1] in ["multi","10","all"]
    if multi:
        amt = min(10, await db.get_berries(uid) // cost)
        if amt < 1: return await message.reply(f"❌ Need {cost}🫐 for 1 pull, {cost*10} for 10!")
        total_cost = amt * cost
    else:
        amt = 1
        total_cost = cost
    bal = await db.get_berries(uid)
    if bal < total_cost:
        return await message.reply(f"❌ Need {total_cost}🫐! You have {bal}🫐")
    await db.remove_berries(uid, total_cost)
    results = []
    for _ in range(amt):
        rarity = random.choices(["3star","4star","5star"], weights=[70, 25, 5])[0]
        char = random.choice(CHARACTERS[rarity])
        await db.add_character(uid, char, rarity)
        await db.inc_user(uid, "wishes")
        results.append(f"{'⭐' if rarity=='5star' else '⭐' if rarity=='4star' else '🎴'} {char}")
    await message.reply(
        f"✨ <b>Wish Results</b> ✨\n\n"
        f"Used: {total_cost}🫐 | Pulls: {amt}\n\n" +
        "\n".join(results) +
        f"\n\n💰 Balance: {await db.get_berries(uid)}🫐"
    )

@Client.on_message(filters.command("collection"))
async def collection_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    chars = await db.get_characters(uid)
    if not chars:
        return await message.reply("📦 No characters yet! Use /wish to pull some!")
    text = "📦 <b>Your Collection</b>\n\n"
    for name, data in sorted(chars.items()):
        rarity = data.get("rarity", "3star")
        icon = "✨" if rarity == "5star" else "⭐" if rarity == "4star" else "🎴"
        fav = " 💍" if data.get("favorite") else ""
        text += f"{icon} <b>{name}</b> x{data['count']}{fav}\n"
    await message.reply(text)

@Client.on_message(filters.command(["favorite","fav"]))
async def fav_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /fav <character name>")
    name = " ".join(message.command[1:])
    uid = message.from_user.id
    db = client.bot_instance.db
    chars = await db.get_characters(uid)
    found = None
    for c in chars:
        if name.lower() in c.lower():
            found = c; break
    if not found:
        return await message.reply("❌ Character not found in your collection.")
    for c in chars:
        chars[c]["favorite"] = (c == found)
    await db.update_user(uid, {"characters": chars, "favorite_char": found})
    await message.reply(f"💍 Set <b>{found}</b> as your favorite!")

@Client.on_message(filters.command(["character","char"]))
async def character_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    u = await db.get_user(uid)
    fav = u.get("favorite_char")
    if not fav:
        return await message.reply("No favorite set. Use /fav <name> to set one.")
    text = f"🌟 <b>Your Favorite</b>\n\n{fav}"
    await message.reply(text)

@Client.on_message(filters.command(["tradechar","trade"]))
async def trade_char_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to trade a character!")
    target = message.reply_to_message.from_user
    if target.id == message.from_user.id:
        return await message.reply("Can't trade with yourself!")
    if len(message.command) < 2:
        return await message.reply("Usage: /tradechar <char_name>")
    name = " ".join(message.command[1:])
    uid = message.from_user.id
    db = client.bot_instance.db
    chars = await db.get_characters(uid)
    if name not in chars:
        return await message.reply(f"❌ You don't have <b>{name}</b>!")
    if chars[name]["count"] < 1:
        return await message.reply(f"❌ You don't own <b>{name}</b>!")
    await db.register_user(target.id, target.first_name)
    target_chars = await db.get_characters(target.id)
    if name in target_chars:
        target_chars[name]["count"] += 1
    else:
        target_chars[name] = {"rarity": chars[name]["rarity"], "count": 1, "favorite": False}
    chars[name]["count"] -= 1
    if chars[name]["count"] <= 0:
        del chars[name]
    await db.update_user(uid, {"characters": chars})
    await db.update_user(target.id, {"characters": target_chars})
    await message.reply(f"🎁 Traded <b>{name}</b> to {target.mention}!")
