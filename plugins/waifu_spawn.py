import random, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from utils.helpers import Helpers

WAIFUS = [
    ("🌸", "Rem"), ("🌸", "Ram"), ("🌸", "Emilia"), ("🌸", "Megumin"), ("🌸", "Aqua"),
    ("🌸", "Darkness"), ("🌸", "Asuna"), ("🌸", "Miku"), ("🌸", "Nezuko"), ("🌸", "Shinobu"),
    ("🌸", "Zero Two"), ("🌸", "Hinata"), ("🌸", "Sakura"), ("🌸", "Rias"), ("🌸", "Akeno"),
    ("🌸", "Yui"), ("🌸", "Chika"), ("🌸", "Kaguya"), ("🌸", "Mai"), ("🌸", "Taiga"),
    ("🌸", "Shana"), ("🌸", "Louise"), ("🌸", "Nagi"), ("🌸", "Kurumi"), ("🌸", "Yoshino"),
    ("🌸", "Miku N"), ("🌸", "Luka"), ("🌸", "Rin"), ("🌸", "Len"), ("🌸", "Teto"),
    ("🌸", "Hatsune M"), ("🌸", "Kagamine R"), ("🌸", "IA"), ("🌸", "Gumi"),
    ("🌸", "Alice"), ("🌸", "Yuno"), ("🌸", "Mirai"), ("🌸", "Miyuki"), ("🌸", "Eru"),
    ("🌸", "Yukino"), ("🌸", "Yotsuba"), ("🌸", "Ichika"), ("🌸", "Nino"), ("🌸", "Miku N"),
    ("🌸", "Itsuki"), ("🌸", "Chitoge"), ("🌸", "Kosaki"), ("🌸", "Marika"),
    ("🌸", "Shinobu K"), ("🌸", "Hitagi"), ("🌸", "Mayoi"), ("🌸", "Karen"),
    ("🌸", "Sento"), ("🌸", "Airi"), ("🌸", "Rize"), ("🌸", "Cocoa"), ("🌸", "Chino"),
    ("🌸", "Syaro"), ("🌸", "Maya"), ("🌸", "Megu"), ("🌸", "Aoi"), ("🌸", "Akari"),
    ("🌸", "Kyoko"), ("🌸", "Yui H"), ("🌸", "Ui"), ("🌸", "Azusa"), ("🌸", "Mio"),
    ("🌸", "Ritsu"), ("🌸", "Tsumugi"), ("🌸", "Yuki"), ("🌸", "Mikuru"), ("🌸", "Haruhi"),
]

WAIFU_IMAGES = {
    "Rem": None, "Ram": None, "Emilia": None, "Megumin": None, "Aqua": None,
    "Darkness": None, "Asuna": None, "Miku": None, "Nezuko": None, "Shinobu": None,
    "Zero Two": None, "Hinata": None, "Sakura": None, "Rias": None, "Akeno": None,
    "Yui": None, "Chika": None, "Kaguya": None, "Mai": None, "Taiga": None,
    "Kurumi": None, "Hatsune M": None, "Yuno": None, "Mirai": None, "Nino": None,
}
WAIFU_FALLBACK_IMG = "https://i.imgur.com/HHL1Z7I.jpeg"

WAIFU_API_URL = "https://api.waifu.im/search/?selected_tags=waifu&width=512"

async def get_waifu_image(name: str) -> str:
    url = WAIFU_IMAGES.get(name)
    if url: return url
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(WAIFU_API_URL, timeout=5) as resp:
                data = await resp.json()
                return data["images"][0]["url"]
    except:
        return WAIFU_FALLBACK_IMG

active_waifus = {}
waifu_counters = {}

@Client.on_message(filters.group & filters.text & ~filters.service, group=7)
async def waifu_spawn_tracker(client: Client, message: Message):
    cid = message.chat.id
    settings = await client.bot_instance.db.get_chat_settings(cid)
    if not settings.get("spawn_monsters", True): return
    waifu_counters[cid] = waifu_counters.get(cid, 0) + 1
    if waifu_counters[cid] >= 40:
        waifu_counters[cid] = 0
        await spawn_waifu(client, cid)

async def spawn_waifu(client: Client, chat_id: int):
    emoji, name = random.choice(WAIFUS)
    wid = f"waifu_{chat_id}_{random.randint(1000,9999)}"
    rarity_roll = random.random()
    if rarity_roll < 0.05: rarity = "💎 Legendary"
    elif rarity_roll < 0.20: rarity = "✨ Rare"
    else: rarity = "🌸 Common"
    active_waifus[wid] = {"name": name, "emoji": emoji, "rarity": rarity, "chat_id": chat_id, "caught": False}
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"🌸 Catch {name}!", callback_data=f"waifu_catch_{wid}")
    ]])
    caption = Helpers.format_msg(
        f"🌸 <b>A Wild Waifu Appeared!</b>\n\n"
        f"{emoji} <b>{name}</b>\n"
        f"⭐ Rarity: {rarity}\n\n"
        f"First to tap catches her! 🏃"
    )
    img_url = await get_waifu_image(name)
    is_photo = False
    try:
        msg = await client.send_photo(chat_id, img_url, caption=caption, reply_markup=kb)
        is_photo = True
    except:
        msg = await client.send_message(chat_id, caption, reply_markup=kb)
    await asyncio.sleep(60)
    if wid in active_waifus:
        if not active_waifus[wid]["caught"]:
            try:
                if is_photo:
                    await msg.edit_caption(caption=f"🌸 <b>{name}</b> ran away... 💔")
                else:
                    await msg.edit(f"🌸 <b>{name}</b> ran away... 💔")
            except: pass
        del active_waifus[wid]

@Client.on_callback_query(filters.create(lambda _, __, q: q.data.startswith("waifu_")))
async def waifu_catch_cb(client: Client, query: CallbackQuery):
    data = query.data.split("_", 2)
    if len(data) < 3: return
    action, wid = data[1], data[2]
    if action != "catch": return
    waifu = active_waifus.get(wid)
    if not waifu: return await query.answer("Gone! Waifu ran away 💔", show_alert=True)
    if waifu["caught"]: return await query.answer("Already caught by someone else! ⚡", show_alert=True)
    waifu["caught"] = True
    uid = query.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, query.from_user.first_name)
    name = waifu["name"]
    rarity = waifu["rarity"]
    points = {"💎 Legendary": 100, "✨ Rare": 50, "🌸 Common": 20}[rarity]
    reward = {"💎 Legendary": 500, "✨ Rare": 200, "🌸 Common": 50}[rarity]
    await db.add_character(uid, name, rarity)
    await db.add_berries_raw(uid, reward)
    await db.add_log("waifu_catch", {"user": uid, "name": name, "rarity": rarity})
    text = (
        f"🎉 <b>Waifu Caught!</b>\n\n"
        f"{query.from_user.mention} caught <b>{name}</b>!\n"
        f"{rarity} +{points}pts\n"
        f"💰 +{reward}🫐\n\n"
        f"📦 Check /collection to see all your waifus!"
    )
    await query.message.edit(text)
    await query.answer(f"🌸 Caught {name}!", show_alert=True)
    del active_waifus[wid]

@Client.on_message(filters.command(["waifus","spawnwaifu"]))
async def waifu_list_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    chars = await db.get_characters(uid)
    waifus = {k: v for k, v in chars.items() if any(w[1] == k for w in WAIFUS)}
    if not waifus:
        return await message.reply("🌸 No waifus caught yet! Wait for one to spawn in chat! 🌸")
    text = "🌸 <b>Your Waifus</b>\n\n"
    for name, data in sorted(waifus.items()):
        rarity = data.get("rarity", "🌸 Common")
        fav = " 💍" if data.get("favorite") else ""
        text += f"{rarity.split()[0]} <b>{name}</b> x{data['count']}{fav}\n"
    await message.reply(text)
