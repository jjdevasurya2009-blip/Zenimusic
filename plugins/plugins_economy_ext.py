import random, asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import Config
from utils.buttons import Buttons
from utils.helpers import Helpers

# ==================== BANK ====================

@Client.on_message(filters.command(["bank","balance"]))
async def bank_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    interest = await db.apply_bank_interest(uid)
    u = await db.get_user(uid)
    wallet = u.get("berries", 0)
    bank = u.get("bank", 0)
    text = (
        f"🏦 <b>Bank</b>\n\n"
        f"👛 Wallet: <b>{wallet}🫐</b>\n"
        f"🏛️ Bank: <b>{bank}🫐</b>\n"
        f"📈 Interest: <b>5% daily</b>\n"
    )
    if interest:
        text += f"✨ Collected interest: <b>+{interest}🫐</b>"
    else:
        text += f"⏳ Already collected today's interest!"
    await message.reply(text)

@Client.on_message(filters.command("deposit"))
async def deposit_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    if len(message.command) < 2:
        return await message.reply("Usage: /deposit <amount> or /deposit all")
    amt_str = message.command[1]
    if amt_str == "all":
        amt = await db.get_berries(uid)
    else:
        try: amt = int(amt_str)
        except: return await message.reply("❌ Invalid amount!")
    if amt < 1: return await message.reply("❌ Amount must be positive!")
    if await db.bank_deposit(uid, amt):
        await message.reply(f"✅ Deposited <b>{amt}🫐</b>!\n💰 Bank: {await db.bank_balance(uid)}🫐")
    else:
        await message.reply(f"❌ You don't have {amt}🫐 in wallet!")

@Client.on_message(filters.command("withdraw"))
async def withdraw_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    if len(message.command) < 2:
        return await message.reply("Usage: /withdraw <amount> or /withdraw all")
    amt_str = message.command[1]
    if amt_str == "all":
        amt = await db.bank_balance(uid)
    else:
        try: amt = int(amt_str)
        except: return await message.reply("❌ Invalid amount!")
    if amt < 1: return await message.reply("❌ Amount must be positive!")
    if await db.bank_withdraw(uid, amt):
        await message.reply(f"✅ Withdrew <b>{amt}🫐</b>!\n💰 Wallet: {await db.get_berries(uid)}🫐")
    else:
        await message.reply(f"❌ You don't have {amt}🫐 in bank!")

# ==================== LOTTERY ====================

@Client.on_message(filters.command(["lottery","lotto"]))
async def lottery_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    pool = await db.get_lottery_pool()
    u = await db.get_user(uid)
    tickets = u.get("lottery_tickets", 0)
    text = (
        f"🎰 <b>Lottery</b>\n\n"
        f"🏆 Prize Pool: <b>{pool}🫐</b>\n"
        f"🎟️ Your Tickets: <b>{tickets}</b>\n\n"
        f"Buy tickets: /buyticket <count>\n"
        f"Cost: 50🫐 per ticket"
    )
    await message.reply(text)

@Client.on_message(filters.command(["buyticket","buytickets"]))
async def buy_ticket_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    count = 1
    if len(message.command) > 1:
        try: count = max(1, min(100, int(message.command[1])))
        except: return await message.reply("Usage: /buyticket <count>")
    cost = count * 50
    bal = await db.get_berries(uid)
    if bal < cost:
        return await message.reply(f"❌ Need {cost}🫐, you have {bal}🫐")
    if await db.lottery_buy_ticket(uid, count):
        await message.reply(f"✅ Bought <b>{count}</b> ticket(s) for {cost}🫐!\n🎟️ Total: {(await db.get_user(uid)).get('lottery_tickets', 0)}")

# ==================== DAILY LOTTERY DRAW ====================

async def lottery_draw(client: Client):
    db = client.bot_instance.db
    pool = await db.get_lottery_pool()
    if pool < 100: return
    cursor = db.db.users.find({"lottery_tickets": {"$gt": 0}})
    participants = await cursor.to_list(length=None)
    if not participants: return
    total_tickets = sum(p.get("lottery_tickets", 0) for p in participants)
    if total_tickets == 0: return
    rand = random.randint(1, total_tickets)
    cumulative = 0
    winner = None
    for p in participants:
        cumulative += p.get("lottery_tickets", 0)
        if rand <= cumulative:
            winner = p
            break
    if not winner: winner = random.choice(participants)
    wid = winner["user_id"]
    share = int(pool * 0.9)
    owner_share = pool - share
    await db.add_berries_raw(wid, share)
    await db.add_berries_raw(Config.OWNER_ID, owner_share)
    await db.inc_user(wid, "lottery_wins")
    await db.db.users.update_many({}, {"$set": {"lottery_tickets": 0}})
    await db.reset_lottery_pool()
    try: await client.send_message(wid, Helpers.format_msg(f"🎉 <b>Lottery Won!</b>\n\nYou won <b>{share}🫐</b> in the daily lottery draw!"))
    except: pass

# ==================== ITEM USAGE ====================

ITEM_EFFECTS = {
    "🍫 Chocolate": {"berries": 10, "msg": "You ate the chocolate! +10🫐 energy!"},
    "🍺 Beer": {"xp": 5, "msg": "You drank the beer! +5XP!"},
    "💕 Girlfriend": {"daily": 50, "msg": "Your virtual gf sends you love! +50🫐 daily!"},
    "⚔️ Sword": {"battle_buff": True, "msg": "You equip the sword! +5 damage in battles!"},
    "🛡️ Shield": {"battle_buff": True, "msg": "You equip the shield! +10 HP in battles!"},
    "💊 HP Potion": {"heal": True, "msg": "You drink the potion! Feeling refreshed!"},
    "🎴 Mystery Box": {"mystery": True, "msg": ""},
}

@Client.on_message(filters.command("use"))
async def use_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /use <item name>\nInventory: /inventory or /inv")
    name = " ".join(message.command[1:])
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    inv = await db.get_inventory(uid)
    matched = None
    for item in inv:
        if name.lower() in item.lower():
            matched = item; break
    if not matched:
        return await message.reply(f"❌ You don't have <b>{name}</b>! Check /inv")
    if not await db.remove_from_inventory(uid, matched):
        return await message.reply("❌ Error using item!")
    effect = ITEM_EFFECTS.get(matched, {})
    msg = effect.get("msg", f"Used <b>{matched}</b>!")
    if "berries" in effect:
        await db.add_berries_raw(uid, effect["berries"])
    if "xp" in effect:
        await db.inc_user(uid, "xp", effect["xp"])
    if effect.get("mystery"):
        reward = random.choice([100, 200, 300, 500, 1000])
        await db.add_berries_raw(uid, reward)
        msg = f"🎁 You opened the Mystery Box and found <b>{reward}🫐</b>!"
    await message.reply(f"✅ {msg}\n💰 Balance: {await db.get_berries(uid)}🫐")

@Client.on_message(filters.command(["inventory","inv"]))
async def inventory_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    inv = await db.get_inventory(uid)
    if not inv:
        return await message.reply("🎒 <b>Inventory</b>\n\nEmpty! Buy items from /shop")
    text = "🎒 <b>Inventory</b>\n\n"
    for item, qty in inv.items():
        text += f"• {item} x{qty}\n"
    text += "\nUse /use <item> to use an item!"
    await message.reply(text)

# ==================== XP / LEVELS ====================

@Client.on_message(filters.group & filters.text & ~filters.service, group=4)
async def xp_tracker(client: Client, message: Message):
    uid = message.from_user.id
    if message.from_user.is_bot: return
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    new_level = await db.add_xp(uid, random.randint(3, 8))
    if new_level:
        await message.reply(f"🎉 <b>LEVEL UP!</b>\n\n{message.from_user.mention} reached <b>Level {new_level}</b>!")
    await db.apply_bank_interest(uid)

@Client.on_message(filters.command(["level","rank","xp"]))
async def level_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    u = await db.get_user(uid)
    if not u: return await message.reply("Not registered!")
    xp = u.get("xp", 0)
    level = u.get("level", 1)
    needed = level * 100
    text = (
        f"📊 <b>Your Stats</b>\n\n"
        f"⭐ Level: <b>{level}</b>\n"
        f"📈 XP: {xp}/{needed}\n"
        f"💬 Messages: {u.get('total_messages', 0)}\n"
        f"🏆 Wishes: {u.get('wishes', 0)}\n"
        f"⚔️ Monster Kills: {u.get('monster_kills', 0)}\n"
        f"🎟️ Lottery Wins: {u.get('lottery_wins', 0)}"
    )
    achs = u.get("achievements", [])
    if achs:
        text += f"\n\n🏅 Achievements: {len(achs)}"
    await message.reply(text)

@Client.on_message(filters.command(["achievements","ach","badges"]))
async def achievements_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    u = await db.get_user(uid)
    achs = u.get("achievements", []) if u else []
    all_ach = [
        "💰 First 1000🫐", "🎰 Lottery Winner", "⚔️ Monster Slayer",
        "💍 Married", "⭐ Premium User", "🎴 Collector (10 chars)",
        "🎮 Game Champion", "🎵 Music Lover", "💀 Killer", "❤️ Reviver",
        "📅 7-Day Streak", "🏦 Banker (1000🫐 saved)", "🎲 Gambler (10 bets)",
    ]
    text = "🏅 <b>Achievements</b>\n\n"
    for a in all_ach:
        icon = "✅" if a in achs else "❌"
        text += f"{icon} {a}\n"
    await message.reply(text)
