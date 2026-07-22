from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from datetime import datetime, timedelta
from utils.buttons import Buttons

@Client.on_message(filters.command(["shop","store"]))
async def shop_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db
    await db.register_user(uid, message.from_user.first_name)
    cfg = await db.get_bot_config()
    items = cfg.get("shop_items", {})
    balance = await db.get_berries(uid)
    text = f"🛒 <b>Berry Shop</b>\n\n💰 Your Balance: <b>{balance}🫐</b>\n\n"
    buttons = []
    for name, data in items.items():
        text += f"<b>{name}</b> — {data['price']}🫐\n└ {data['description']}\n\n"
        buttons.append([InlineKeyboardButton(f"Buy {name} ({data['price']}🫐)", callback_data=f"shop_buy_{name}")])
    buttons.append([InlineKeyboardButton("🎒 My Inventory", callback_data="shop_inventory")])
    buttons.append([InlineKeyboardButton("◀️ Back", callback_data="back_start")])
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.create(lambda _, __, q: q.data.startswith("shop_")))
async def shop_callbacks(client: Client, query):
    data = query.data
    uid = query.from_user.id
    db = client.bot_instance.db
    if data == "shop_inventory":
        inv = await db.get_inventory(uid)
        text = "🎒 <b>Your Inventory</b>\n\n"
        if inv:
            for item, qty in inv.items():
                text += f"• {item} x{qty}\n"
        else:
            text += "Empty. Buy items from /shop!"
        await query.message.edit(text, reply_markup=Buttons.back_button("menu_shop"))
        return await query.answer()
    if data.startswith("shop_buy_"):
        item_name = data.split("_", 2)[2]
        cfg = await db.get_bot_config()
        items = cfg.get("shop_items", {})
        if item_name not in items:
            return await query.answer("❌ Item not found!", show_alert=True)
        item = items[item_name]
        price = item["price"]
        balance = await db.get_berries(uid)
        if balance < price:
            return await query.answer(f"❌ Need {price}🫐, you have {balance}🫐", show_alert=True)
        # Handle premium purchases specially
        if item_name.startswith("⭐ Premium"):
            days = 1 if "1D" in item_name else 7
            prem_until = datetime.now() + timedelta(days=days)
            u = await db.get_user(uid)
            existing = u.get("premium_expiry")
            if existing and existing > datetime.now():
                prem_until = existing + timedelta(days=days)
            await db.remove_berries(uid, price)
            await db.update_user(uid, {"is_premium": True, "premium_expiry": prem_until})
            await query.message.edit(
                f"⭐ <b>Premium Activated!</b>\n\n{days} day(s) of premium added!\n"
                f"Expires: {prem_until.strftime('%Y-%m-%d %H:%M')}\n"
                f"💰 Remaining: {await db.get_berries(uid)}🫐",
                reply_markup=Buttons.back_button("back_start")
            )
            return await query.answer(f"⭐ Premium +{days}d!")
        else:
            await db.remove_berries(uid, price)
            await db.add_to_inventory(uid, item_name)
            await query.message.edit(
                f"✅ <b>Purchased!</b>\n\n"
                f"You bought <b>{item_name}</b> for {price}🫐!\n"
                f"💰 Remaining: {await db.get_berries(uid)}🫐\n"
                f"Check /shop or inventory!",
                reply_markup=Buttons.back_button("shop")
            )
            return await query.answer(f"✅ Bought {item_name}!")
