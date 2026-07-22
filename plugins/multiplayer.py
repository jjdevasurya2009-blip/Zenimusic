import random
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from utils.buttons import Buttons

ROB_COST = 50
ROB_MIN_WIN = 50
ROB_MAX_WIN = 200
ROB_FAIL_PENALTY = 30
KILL_COST = 100
REVIVE_COST = 75

@Client.on_message(filters.command("daily"))
async def daily_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    u = await db.get_user(uid)
    last = u.get("last_daily")
    now = datetime.now()
    if last and datetime.fromisoformat(last).date() == now.date():
        return await message.reply("⏳ You already claimed your daily reward today!\nCome back tomorrow.")
    streak = u.get("daily_streak", 0) + 1
    base = 200
    bonus = min(streak * 10, 100)
    total = base + bonus
    prem = await db.is_premium(uid)
    if prem:
        total = int(total * 1.5)
    await db.add_berries(uid, total)
    await db.update_user(uid, {"last_daily": now.isoformat(), "daily_streak": streak})
    await message.reply(
        f"📅 <b>Daily Reward</b>\n\n"
        f"💰 <b>+{total}🫐</b>\n"
        f"🔥 Streak: {streak} day(s)\n"
        f"{'⭐ Premium bonus x1.5!' if prem else ''}\n"
        f"Come back tomorrow for more!"
    )

@Client.on_message(filters.command("rob") & filters.group)
async def rob_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to rob them!")
    uid = message.from_user.id
    target = message.reply_to_message.from_user
    if target.id == uid:
        return await message.reply("You can't rob yourself!")
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    await db.register_user(target.id, target.first_name)
    balance = await db.get_berries(uid)
    if balance < ROB_COST:
        return await message.reply(f"❌ You need {ROB_COST}🫐 to attempt a robbery!")
    target_bal = await db.get_berries(target.id)
    if target_bal < ROB_MIN_WIN:
        return await message.reply(f"❌ {target.first_name} is too poor to rob! (<{ROB_MIN_WIN}🫐)")
    success = random.random() < 0.45
    await db.remove_berries(uid, ROB_COST)
    if success:
        stolen = random.randint(ROB_MIN_WIN, min(ROB_MAX_WIN, target_bal))
        await db.remove_berries(target.id, stolen)
        await db.add_berries(uid, stolen)
        await db.inc_user(uid, "rob_success")
        await message.reply(
            f"🔫 <b>Robbery Successful!</b>\n\n"
            f"{message.from_user.mention} robbed {target.mention} for <b>{stolen}🫐</b>!\n"
            f"💰 Your balance: {await db.get_berries(uid)}🫐"
        )
    else:
        fine = ROB_FAIL_PENALTY
        await db.inc_user(uid, "rob_fail")
        await message.reply(
            f"🚔 <b>Robbery Failed!</b>\n\n"
            f"{message.from_user.mention} got caught robbing {target.mention}!\n"
            f"Paid {fine}🫐 bail.\n"
            f"💰 Balance: {await db.get_berries(uid)}🫐"
        )

@Client.on_message(filters.command("kill") & filters.group)
async def kill_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to kill them!")
    uid = message.from_user.id
    target = message.reply_to_message.from_user
    if target.id == uid:
        return await message.reply("You can't kill yourself! Use /suicide if you want.")
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    await db.register_user(target.id, target.first_name)
    balance = await db.get_berries(uid)
    if balance < KILL_COST:
        return await message.reply(f"❌ You need {KILL_COST}🫐 to kill someone!")
    target_data = await db.get_user(target.id)
    if not target_data.get("alive", True):
        return await message.reply(f"💀 {target.first_name} is already dead! Use /revive first.")
    success = random.random() < 0.4
    await db.remove_berries(uid, KILL_COST)
    if success:
        await db.update_user(target.id, {"alive": False})
        await db.inc_user(uid, "kills")
        await db.inc_user(target.id, "deaths")
        reward = 75
        await db.add_berries(uid, reward)
        await message.reply(
            f"💀 <b>MURDER!</b>\n\n"
            f"{message.from_user.mention} killed {target.mention}!\n"
            f"{target.first_name} is now dead. Use /revive to bring them back.\n"
            f"💰 Killer got {reward}🫐 bounty!"
        )
    else:
        await message.reply(
            f"🛡️ <b>Missed!</b>\n\n"
            f"{message.from_user.mention} tried to kill {target.mention} but failed!\n"
            f"Lost {KILL_COST}🫐."
        )

@Client.on_message(filters.command("revive") & filters.group)
async def revive_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to revive them!")
    uid = message.from_user.id
    target = message.reply_to_message.from_user
    db = client.bot_instance.db
    balance = await db.get_berries(uid)
    if balance < REVIVE_COST:
        return await message.reply(f"❌ Need {REVIVE_COST}🫐 to revive!")
    target_data = await db.get_user(target.id)
    if target_data.get("alive", True):
        return await message.reply(f"❌ {target.first_name} is already alive!")
    await db.remove_berries(uid, REVIVE_COST)
    await db.update_user(target.id, {"alive": True})
    await db.inc_user(uid, "revives")
    await message.reply(
        f"❤️ <b>Revived!</b>\n\n"
        f"{message.from_user.mention} revived {target.mention}!\n"
        f"{target.first_name} is back to life!\n"
        f"💰 {await db.get_berries(uid)}🫐 remaining."
    )

@Client.on_message(filters.command(["profile","stats","me"]))
async def profile_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    u = await db.get_user(uid)
    if not u:
        return await message.reply("You're not registered yet! Use any command.")
    text = (
        f"👤 <b>Profile</b>\n\n"
        f"Name: {u.get('name', '?')}\n"
        f"🫐 Berries: <b>{u.get('berries', 0)}</b>\n"
        f"⭐ Premium: {'✅' if u.get('is_premium') else '❌'}\n"
        f"❤️ Status: {'Alive' if u.get('alive', True) else '💀 Dead'}\n"
        f"💍 Married: {'✅' if u.get('married_to') else '❌'}\n\n"
        f"<b>Stats</b>\n"
        f"🎮 Games: {u.get('games_played',0)} | Won: {u.get('games_won',0)}\n"
        f"🔫 Robs: {u.get('rob_success',0)}✅/{u.get('rob_fail',0)}❌\n"
        f"💀 Kills: {u.get('kills',0)} | Deaths: {u.get('deaths',0)}\n"
        f"❤️ Revives: {u.get('revives',0)}\n"
        f"⚔️ Duels: {u.get('duel_wins',0)}W/{u.get('duel_losses',0)}L\n"
        f"🔥 Streak: {u.get('daily_streak',0)} days\n"
        f"🎵 Songs: {u.get('songs_played',0)}"
    )
    await message.reply(text, reply_markup=Buttons.back_button("back_start"))

@Client.on_message(filters.command("gift"))
async def gift_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to gift them berries!")
    uid = message.from_user.id
    target = message.reply_to_message.from_user
    if target.id == uid:
        return await message.reply("You can't gift yourself!")
    if len(message.command) < 2:
        return await message.reply("Usage: /gift <amount>")
    try: amt = int(message.command[1])
    except: return await message.reply("Amount must be a number!")
    if amt < 10:
        return await message.reply("Minimum gift is 10🫐")
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    await db.register_user(target.id, target.first_name)
    bal = await db.get_berries(uid)
    if bal < amt:
        return await message.reply(f"❌ You only have {bal}🫐!")
    await db.remove_berries(uid, amt)
    await db.add_berries_raw(target.id, amt)
    await message.reply(
        f"🎁 <b>Gift Sent!</b>\n\n"
        f"{message.from_user.mention} gifted <b>{amt}🫐</b> to {target.mention}!"
    )

@Client.on_message(filters.command(["bet","gamble"]))
async def bet_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /bet <amount>\n50/50 chance to double your berries!")
    try: amt = int(message.command[1])
    except: return await message.reply("Amount must be a number!")
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    bal = await db.get_berries(uid)
    if amt < 10:
        return await message.reply("Minimum bet is 10🫐")
    if bal < amt:
        return await message.reply(f"❌ You only have {bal}🫐!")
    win = random.random() < 0.5
    if win:
        await db.add_berries(uid, amt)
        await message.reply(f"🎲 <b>You Won!</b>\n\n💰 +{amt}🫐 (2x)\nNew balance: {await db.get_berries(uid)}🫐")
    else:
        await db.remove_berries(uid, amt)
        await message.reply(f"😢 <b>You Lost!</b>\n\n💸 -{amt}🫐\nNew balance: {await db.get_berries(uid)}🫐")

@Client.on_message(filters.command("duel"))
async def duel_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to duel them!")
    uid = message.from_user.id
    target = message.reply_to_message.from_user
    if target.id == uid:
        return await message.reply("You can't duel yourself!")
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    await db.register_user(target.id, target.first_name)
    bal = await db.get_berries(uid)
    if bal < 50:
        return await message.reply("❌ You need at least 50🫐 to duel!")
    win = random.random() < 0.5
    if win:
        reward = random.randint(30, 80)
        await db.add_berries(uid, reward)
        await db.inc_user(uid, "duel_wins")
        await db.inc_user(target.id, "duel_losses")
        u_data = await db.get_user(uid)
        t_data = await db.get_user(target.id)
        await message.reply(
            f"⚔️ <b>Duel Result</b>\n\n"
            f"{message.from_user.mention} defeated {target.mention}!\n"
            f"💰 Won <b>{reward}🫐</b>\n"
            f"🏆 Record: ⚔️{u_data.get('duel_wins',0)}W/{t_data.get('duel_losses',0)}L"
        )
    else:
        penalty = random.randint(20, 50)
        await db.remove_berries(uid, penalty)
        await db.inc_user(uid, "duel_losses")
        await db.inc_user(target.id, "duel_wins")
        await message.reply(
            f"⚔️ <b>Duel Result</b>\n\n"
            f"{message.from_user.mention} lost to {target.mention}!\n"
            f"💸 Lost <b>{penalty}🫐</b>\n"
            f"Better luck next time!"
        )

@Client.on_message(filters.command(["marry","propose"]))
async def marry_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to propose marriage!")
    uid = message.from_user.id
    target = message.reply_to_message.from_user
    if target.id == uid:
        return await message.reply("You can't marry yourself!")
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    await db.register_user(target.id, target.first_name)
    u1 = await db.get_user(uid)
    u2 = await db.get_user(target.id)
    if u1.get("married_to"):
        return await message.reply("❌ You're already married! Use /divorce first.")
    if u2.get("married_to"):
        return await message.reply("❌ They're already married!")
    bal = await db.get_berries(uid)
    if bal < 1000:
        return await message.reply("❌ You need 1000🫐 to propose!")
    await db.remove_berries(uid, 1000)
    now = datetime.now().isoformat()
    await db.update_user(uid, {"married_to": target.id, "married_since": now})
    await db.update_user(target.id, {"married_to": uid, "married_since": now})
    await message.reply(
        f"💍 <b>Married!</b> 💍\n\n"
        f"{message.from_user.mention} 💕 {target.mention}\n"
        f"Together forever! 💖"
    )

@Client.on_message(filters.command("divorce"))
async def divorce_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    u = await db.get_user(uid)
    spouse_id = u.get("married_to")
    if not spouse_id:
        return await message.reply("❌ You're not married!")
    await db.update_user(uid, {"married_to": None, "married_since": None})
    await db.update_user(spouse_id, {"married_to": None, "married_since": None})
    await message.reply(
        f"💔 <b>Divorced</b>\n\n"
        f"You are no longer married. 💔"
    )

@Client.on_message(filters.command(["spouse","love"]))
async def spouse_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    u = await db.get_user(uid)
    spouse_id = u.get("married_to")
    if not spouse_id:
        return await message.reply("💔 You're not married. Use /marry to propose!")
    try:
        spouse = await client.get_users(spouse_id)
        since = u.get("married_since", "unknown")
        await message.reply(
            f"💕 <b>Your Spouse</b>\n\n"
            f"👤 {spouse.mention}\n"
            f"📅 Married since: {since[:10] if since != 'unknown' else 'unknown'}\n"
            f"💖 Love is beautiful!"
        )
    except:
        await message.reply(f"💕 Married to user ID: {spouse_id}")

@Client.on_message(filters.command(["rich","leaderboard"]))
async def rich_cmd(client: Client, message: Message):
    db = client.bot_instance.db
    top = await db.get_top_users("berries", 15)
    text = "💰 <b>Richest Users</b>\n\n"
    for i, u in enumerate(top, 1):
        name = u.get("name", f"User{u['user_id']}")[:20]
        badge = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{badge} {name} — {u.get('berries', 0)}🫐\n"
    await message.reply(text, reply_markup=Buttons.back_button("back_start"))
