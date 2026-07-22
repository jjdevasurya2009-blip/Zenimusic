import random, asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from utils.helpers import Helpers

MONSTERS = {
    "slime": {"name": "💧 Slime", "hp": 50, "reward": 30, "emoji": "💧", "min_dmg": 5, "max_dmg": 15},
    "goblin": {"name": "👺 Goblin", "hp": 80, "reward": 50, "emoji": "👺", "min_dmg": 8, "max_dmg": 20},
    "wolf": {"name": "🐺 Wolf", "hp": 120, "reward": 75, "emoji": "🐺", "min_dmg": 10, "max_dmg": 25},
    "skeleton": {"name": "💀 Skeleton", "hp": 150, "reward": 100, "emoji": "💀", "min_dmg": 12, "max_dmg": 30},
    "orc": {"name": "👹 Orc", "hp": 200, "reward": 150, "emoji": "👹", "min_dmg": 15, "max_dmg": 35},
    "dragon": {"name": "🐉 Dragon", "hp": 400, "reward": 300, "emoji": "🐉", "min_dmg": 20, "max_dmg": 50},
}

MONSTER_IMAGES = {
    "slime": None,
    "goblin": None,
    "wolf": None,
    "skeleton": None,
    "orc": None,
    "dragon": None,
}
MONSTER_FALLBACK_IMG = "https://i.imgur.com/t0w4pPJ.png"

async def get_monster_image(mtype: str) -> str:
    url = MONSTER_IMAGES.get(mtype)
    if url: return url
    return MONSTER_FALLBACK_IMG

battles = {}
message_counts = {}

@Client.on_message(filters.group & filters.text & ~filters.service, group=5)
async def track_spawn(client: Client, message: Message):
    cid = message.chat.id
    settings = await client.bot_instance.db.get_chat_settings(cid)
    if not settings.get("spawn_monsters", True): return
    interval = settings.get("spawn_interval", 80)
    message_counts[cid] = message_counts.get(cid, 0) + 1
    if message_counts[cid] >= interval:
        message_counts[cid] = 0
        await spawn_monster(client, cid)

async def spawn_monster(client: Client, chat_id: int):
    mtype = random.choice(list(MONSTERS.keys()))
    m = dict(MONSTERS[mtype])
    bid = f"pve_{chat_id}_{random.randint(1000,9999)}"
    battles[bid] = {"monster": m, "fighters": {}, "chat_id": chat_id, "type": mtype, "started": datetime.now()}
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"⚔️ Fight {m['emoji']}", callback_data=f"pve_fight_{bid}"),
        InlineKeyboardButton(f"🏃 Run", callback_data=f"pve_run_{bid}")
    ]])
    caption = Helpers.format_msg(
        f"⚔️ <b>MONSTER SPAWNED!</b>\n\n"
        f"{m['emoji']} <b>{m['name']}</b>\n"
        f"❤️ HP: {m['hp']} | 🫐 Reward: {m['reward']}\n\n"
        f"Tap fight to battle! Expires in 3 min."
    )
    img_url = await get_monster_image(mtype)
    try:
        await client.send_photo(chat_id, img_url, caption=caption, reply_markup=kb)
    except:
        await client.send_message(chat_id, caption, reply_markup=kb)
    await asyncio.sleep(180)
    if bid in battles: del battles[bid]

@Client.on_callback_query(filters.create(lambda _, __, q: q.data.startswith("pve_")))
async def pve_cb(client: Client, query: CallbackQuery):
    data = query.data
    parts = data.split("_", 2)
    action = parts[1]
    bid = parts[2]
    battle = battles.get(bid)
    if not battle:
        return await query.answer("Battle expired!", show_alert=True)
    uid = query.from_user.id
    uid_str = str(uid)
    db = client.bot_instance.db
    await db.register_user(uid, query.from_user.first_name)
    if action == "fight":
        ubal = await db.get_berries(uid)
        if ubal < 10:
            return await query.answer("Need 10🫐 to fight!", show_alert=True)
        await db.remove_berries(uid, 10)
        await query.answer("⚔️ Attacking!")
        inv = await db.get_inventory(uid)
        sword_bonus = (inv.get("⚔️ Sword", 0) * 5)
        dmg = random.randint(MONSTERS[battle["type"]]["min_dmg"], MONSTERS[battle["type"]]["max_dmg"]) + sword_bonus
        crit = ""
        if random.random() < 0.15:
            dmg = int(dmg * 2)
            crit = "💥 CRIT! "
        battle["monster"]["hp"] -= dmg
        await db.inc_user(uid, "monster_damage", dmg)
        battle["fighters"][uid_str] = battle["fighters"].get(uid_str, 0) + dmg
        if battle["monster"]["hp"] <= 0:
            reward = battle["monster"]["reward"]
            bonus = int(reward * 0.2 * (len(battle["fighters"]) - 1))
            share = reward + bonus
            if share < 0: share = reward
            await db.add_berries(uid, share)
            await db.inc_user(uid, "monster_kills")
            await db.add_log("monster_kill", {"user": uid, "monster": battle["type"], "reward": share})
            dmg_board = "\n".join([f"• <code>{n[:12]}</code>: {d}dmg" for n, d in sorted(battle["fighters"].items(), key=lambda x: -x[1])])
            text = (
                f"🎉 <b>Monster Defeated!</b>\n\n"
                f"{crit}{query.from_user.mention} landed the final blow ({dmg}dmg)!\n"
                f"🏆 Won <b>{share}🫐</b>\n\n"
                f"<b>Damage Board:</b>\n{dmg_board}"
            )
            await query.message.edit(text)
            del battles[bid]
        else:
            mdmg = random.randint(3, 10)
            await db.remove_berries(uid, mdmg)
            hp_left = battle["monster"]["hp"]
            await query.message.edit(
                f"⚔️ <b>{battle['monster']['name']}</b>\n"
                f"❤️ HP: {hp_left}/{MONSTERS[battle['type']]['hp']}\n\n"
                f"{crit}{query.from_user.first_name} dealt {dmg}dmg!\n"
                f"💢 Monster retaliates! -{mdmg}🫐\n\n"
                f"⚔️ Tap fight to keep going!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⚔️ Fight", callback_data=f"pve_fight_{bid}"),
                    InlineKeyboardButton("🏃 Run", callback_data=f"pve_run_{bid}")
                ]])
            )
    elif action == "run":
        if uid_str in battle["fighters"]:
            del battle["fighters"][uid_str]
            await query.answer("🏃 You fled!")
        else:
            await query.answer("You weren't in this fight!")
