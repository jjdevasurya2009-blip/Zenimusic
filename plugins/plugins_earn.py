from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from datetime import datetime, timedelta
from utils.buttons import Buttons

@Client.on_message(filters.command("earn"))
async def earn_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    cfg = await db.get_bot_config()
    links = cfg.get("earn_links", {})
    rates = cfg.get("berry_rates", {})
    buttons = []
    row = []
    for i, (key, url) in enumerate(links.items()):
        rate = rates.get(key, 50)
        label = f"{key.replace('earn','')} 🫐+{rate}"
        row.append(InlineKeyboardButton(label, callback_data=f"earn_click_{key}"))
        if (i+1) % 2 == 0:
            buttons.append(row); row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("🔗 My Referral Link", callback_data="earn_referral")])
    buttons.append([InlineKeyboardButton("📊 My Stats", callback_data="earn_stats")])
    buttons.append([InlineKeyboardButton("◀️ Back", callback_data="back_start")])
    text = (
        f"🫐 <b>Earn Berries</b>\n\n"
        f"Click a button below, visit the link, come back & get berries!\n"
        f"How it works:\n"
        f"1️⃣ Tap an earn button below\n"
        f"2️⃣ Open the link\n"
        f"3️⃣ Come back and use /claim <code>1-5</code> to get 🫐\n\n"
        f"Or share your referral link & earn 50🫐 per referral!"
    )
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command("claim"))
async def claim_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    if len(message.command) < 2:
        return await message.reply("Usage: /claim <earn_number>\nExample: /claim 1")
    num = message.command[1]
    key = f"earn{num}"
    cfg = await db.get_bot_config()
    rates = cfg.get("berry_rates", {})
    if key not in rates:
        return await message.reply("❌ Invalid earn slot. Use 1-5.")
    u = await db.get_user(uid)
    cd = u.get("earn_cooldown")
    if cd and datetime.fromisoformat(cd) > datetime.now():
        remaining = (datetime.fromisoformat(cd) - datetime.now()).seconds
        return await message.reply(f"⏳ Wait {remaining}s before next claim!")
    amount = rates[key]
    await db.add_berries(uid, amount)
    await db.update_user(uid, {"earn_cooldown": (datetime.now() + timedelta(hours=1)).isoformat()})
    await message.reply(f"✅ Claimed <b>{amount}🫐</b> from {key}!\n💰 Balance: {await db.get_berries(uid)}🫐")

@Client.on_message(filters.command("link"))
async def link_cmd(client: Client, message: Message):
    uid = message.from_user.id
    bot_username = (await client.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{uid}"
    text = (
        f"🔗 <b>Your Referral Link</b>\n\n"
        f"Share this link with friends!\n"
        f"When they start the bot, you get <b>50🫐</b>!\n\n"
        f"<code>{ref_link}</code>\n\n"
        f"📊 Referrals: <b>{(await client.bot_instance.db.get_user(uid)).get('referrals', 0)}</b>"
    )
    await message.reply(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={ref_link}")],
        [InlineKeyboardButton("◀️ Back", callback_data="back_start")]
    ]))

@Client.on_callback_query(filters.create(lambda _, __, q: q.data.startswith("earn_")))
async def earn_callbacks(client: Client, query: CallbackQuery):
    data = query.data
    uid = query.from_user.id
    db = client.bot_instance.db
    if data == "earn_stats":
        u = await db.get_user(uid)
        text = (
            f"📊 <b>Your Berry Stats</b>\n\n"
            f"💰 Balance: <b>{u.get('berries', 0)}🫐</b>\n"
            f"📈 Total Earned: <b>{u.get('total_earned', 0)}🫐</b>\n"
            f"👥 Referrals: <b>{u.get('referrals', 0)}</b>\n"
            f"🎮 Games: {u.get('games_played', 0)} | Wins: {u.get('games_won', 0)}\n"
            f"🔫 Robs: {u.get('rob_success', 0)}✅/{u.get('rob_fail', 0)}❌\n"
            f"💀 Kills: {u.get('kills', 0)} | Deaths: {u.get('deaths', 0)}\n"
            f"❤️ Revives: {u.get('revives', 0)}\n"
            f"🎵 Songs Played: {u.get('songs_played', 0)}"
        )
        await query.message.edit(text, reply_markup=Buttons.back_button("back_start"))
        return await query.answer()
    if data == "earn_referral":
        bot_username = (await client.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start=ref_{uid}"
        await query.message.edit(
            f"🔗 <b>Your Referral Link</b>\n\n<code>{ref_link}</code>\n\nShare & earn 50🫐 each!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Share", url=f"https://t.me/share/url?url={ref_link}")],
                [            InlineKeyboardButton("◀️ Back", callback_data="back_start")]
            ])
        )
        return await query.answer()
    if data.startswith("earn_click_"):
        key = data.split("_")[2]
        cfg = await db.get_bot_config()
        links = cfg.get("earn_links", {})
        url = links.get(key, "https://t.me/zenii_X_music_bot")
        rate = cfg.get("berry_rates", {}).get(key, 50)
        await query.message.edit(
            f"🫐 <b>Earn {rate} Berries</b>\n\n"
            f"1. Click the button below\n"
            f"2. Visit the link\n"
            f"3. Come back and use /claim {key.replace('earn','')}\n\n"
            f"Your earn slot: <b>{key}</b> | Reward: <b>{rate}🫐</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"🔗 Open Link {key.replace('earn','')}", url=url)],
                [InlineKeyboardButton("✅ Done! Claim", callback_data=f"earn_claim_{key}")],
                [InlineKeyboardButton("◀️ Back", callback_data="back_start")]
            ])
        )
        return await query.answer()
    if data.startswith("earn_claim_"):
        key = data.split("_")[2]
        cfg = await db.get_bot_config()
        rates = cfg.get("berry_rates", {})
        if key not in rates:
            return await query.answer("❌ Invalid slot!", show_alert=True)
        u = await db.get_user(uid)
        cd = u.get("earn_cooldown")
        if cd and datetime.fromisoformat(cd) > datetime.now():
            rem = (datetime.fromisoformat(cd) - datetime.now()).seconds
            return await query.answer(f"⏳ Wait {rem}s!", show_alert=True)
        amount = rates[key]
        await db.add_berries(uid, amount)
        await db.update_user(uid, {"earn_cooldown": (datetime.now() + timedelta(hours=1)).isoformat()})
        balance = await db.get_berries(uid)
        await query.message.edit(
            f"✅ <b>Claimed {amount}🫐!</b>\n\n💰 Balance: <b>{balance}🫐</b>\n\nCome back in 1 hour for more!",
            reply_markup=Buttons.back_button("back_start")
        )
        return await query.answer(f"✅ +{amount}🫐!", show_alert=True)
