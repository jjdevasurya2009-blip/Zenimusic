import asyncio, random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from utils.buttons import Buttons

@Client.on_message(filters.command(["game","games"]))
async def game_menu(client: Client, message: Message):
    await message.react("🎮")
    text = (
        "🎮 <b>ZENII GAMES</b>\n\n"
        "❌ Tic Tac Toe - Classic 3x3\n"
        "🏓 Connect 4 - Drop discs\n"
        "🎲 2048 - Merge tiles\n"
        "🧩 Word Puzzle - Unscramble\n"
        "❓ Trivia Quiz - Test knowledge\n"
        "🎯 Number Guess - Guess number\n"
        "🤼 Multiplayer - Battle friends!\n\n"
        "Scores tracked on leaderboard!"
    )
    await message.reply(text, reply_markup=Buttons.games_menu())

@Client.on_message(filters.command("ttt"))
async def ttt_cmd(client: Client, message: Message):
    if not hasattr(client, 'bot_instance'): return
    eng = client.bot_instance.game_engine
    result, _ = await eng.start_game(message.chat.id, message.from_user.id, "ttt", message.from_user.first_name)
    await message.react("❌")
    await message.reply(result, reply_markup=Buttons.ttt_board(
        f"{message.chat.id}_ttt_{message.from_user.id}_{id(message)}",
        [" "]*9, "X", str(message.from_user.id), ""
    ))

@Client.on_message(filters.command("trivia"))
async def trivia_cmd(client: Client, message: Message):
    if not hasattr(client, 'bot_instance'): return
    eng = client.bot_instance.game_engine
    result, buttons = await eng.start_game(message.chat.id, message.from_user.id, "trivia")
    await message.react("❓")
    await message.reply(result, reply_markup=buttons)

@Client.on_message(filters.command("word"))
async def word_cmd(client: Client, message: Message):
    if not hasattr(client, 'bot_instance'): return
    eng = client.bot_instance.game_engine
    result, buttons = await eng.start_game(message.chat.id, message.from_user.id, "word")
    await message.react("🧩")
    await message.reply(result, reply_markup=buttons)

@Client.on_message(filters.command("2048"))
async def game_2048_cmd(client: Client, message: Message):
    if not hasattr(client, 'bot_instance'): return
    eng = client.bot_instance.game_engine
    result, buttons = await eng.start_game(message.chat.id, message.from_user.id, "2048")
    await message.react("🎲")
    await message.reply(result, reply_markup=buttons)

@Client.on_message(filters.command("connect4"))
async def c4_cmd(client: Client, message: Message):
    if not hasattr(client, 'bot_instance'): return
    eng = client.bot_instance.game_engine
    result, _ = await eng.start_game(message.chat.id, message.from_user.id, "c4", message.from_user.first_name)
    await message.react("🏓")
    await message.reply(result)

@Client.on_message(filters.command("number"))
async def number_cmd(client: Client, message: Message):
    if not hasattr(client, 'bot_instance'): return
    eng = client.bot_instance.game_engine
    result, buttons = await eng.start_game(message.chat.id, message.from_user.id, "number")
    await message.react("🎯")
    await message.reply(result, reply_markup=buttons)

@Client.on_message(filters.command(["leaderboard","lb","scores"]))
async def lb_cmd(client: Client, message: Message):
    if not hasattr(client, 'bot_instance'): return
    text = await client.bot_instance.game_engine.get_leaderboard()
    await message.react("🏆")
    await message.reply(text, reply_markup=Buttons.back_button("menu_games"))

@Client.on_message(filters.command(["rps","rockpaperscissors"]))
async def rps_cmd(client: Client, message: Message):
    await message.react("🪨")
    await message.reply(
        "🪨 <b>Rock Paper Scissors</b>\n\nChoose:",
        reply_markup=Buttons.multiplayer_menu()
    )

@Client.on_message(filters.command(["dice","roll"]))
async def dice_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db if hasattr(client, 'bot_instance') else None
    args = message.command[1:]
    target = 6
    bet = 0
    if args:
        try:
            if len(args) >= 2:
                target = max(2, min(100, int(args[0])))
                bet = max(0, int(args[1]))
            else:
                val = int(args[0])
                if 2 <= val <= 100:
                    target = val
                elif val >= 10:
                    bet = val
        except: pass
    if bet > 0 and db:
        await db.register_user(uid, message.from_user.first_name)
        bal = await db.get_berries(uid)
        if bet < 10: return await message.reply("Min bet is 10🫐")
        if bal < bet: return await message.reply(f"❌ You only have {bal}🫐!")
        await db.remove_berries(uid, bet)
    result = random.randint(1, target)
    dice_map = {1:"⚀",2:"⚁",3:"⚂",4:"⚃",5:"⚄",6:"⚅"}
    display = dice_map.get(result, str(result))
    text = f"🎲 <b>Dice</b> (1-{target})\n\n<b>Result:</b> {display} {result}"
    if bet > 0 and db:
        win_target = target // 2
        if result >= win_target:
            winnings = bet * 2
            await db.add_berries(uid, winnings)
            text += f"\n\n🎉 <b>You won {winnings}🫐!</b>"
        else:
            text += f"\n\n😢 <b>Lost {bet}🫐</b>"
        text += f"\n💰 Balance: {await db.get_berries(uid)}🫐"
    await message.react("🎲")
    await message.reply(text)

@Client.on_message(filters.command("dart"))
async def dart_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db if hasattr(client, 'bot_instance') else None
    bet = 0
    if len(message.command) > 1:
        try: bet = max(0, int(message.command[1]))
        except: pass
    if bet > 0 and db:
        await db.register_user(uid, message.from_user.first_name)
        bal = await db.get_berries(uid)
        if bet < 10: return await message.reply("Min bet is 10🫐")
        if bal < bet: return await message.reply(f"❌ You only have {bal}🫐!")
        await db.remove_berries(uid, bet)
    sent = await message.reply_dice(emoji="🎯")
    await asyncio.sleep(2.5)
    val = sent.dice.value
    if bet > 0 and db:
        mult = {1: 0, 2: 0, 3: 0, 4: 1.5, 5: 2, 6: 3}.get(val, 0)
        if mult > 0:
            won = int(bet * mult)
            await db.add_berries(uid, won)
            text = f"🎯 <b>Dart</b>\n\nScore: {val}\n🎉 Won <b>{won}🫐</b>!"
        else:
            text = f"🎯 <b>Dart</b>\n\nScore: {val}\n😢 Lost <b>{bet}🫐</b>"
        text += f"\n💰 Balance: {await db.get_berries(uid)}🫐"
    else:
        text = f"🎯 <b>Dart</b>\n\nScore: {val}"
    await message.reply(text)

@Client.on_message(filters.command(["flip","coin"]))
async def flip_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db if hasattr(client, 'bot_instance') else None
    bet = 0
    if len(message.command) > 1:
        try: bet = int(message.command[-1])
        except: pass
    if bet > 0 and db:
        await db.register_user(uid, message.from_user.first_name)
        bal = await db.get_berries(uid)
        if bet < 10: return await message.reply("Min bet is 10🫐")
        if bal < bet: return await message.reply(f"❌ You only have {bal}🫐!")
        await db.remove_berries(uid, bet)
    result = random.choice(["Heads","Tails"])
    text = f"🪙 <b>Coin Flip</b>\n\n<b>Result:</b> {result}"
    if bet > 0 and db:
        win = random.random() < 0.5
        if win:
            winnings = bet * 2
            await db.add_berries(uid, winnings)
            text += f"\n\n🎉 <b>You won {winnings}🫐!</b>"
        else:
            text += f"\n\n😢 <b>Lost {bet}🫐</b>"
        text += f"\n💰 Balance: {await db.get_berries(uid)}🫐"
    await message.react("🪙")
    await message.reply(text)

@Client.on_message(filters.command("slots"))
async def slots_cmd(client: Client, message: Message):
    uid = message.from_user.id
    db = client.bot_instance.db if hasattr(client, 'bot_instance') else None
    bet = 0
    if len(message.command) > 1:
        try: bet = int(message.command[-1])
        except: pass
    if bet > 0 and db:
        await db.register_user(uid, message.from_user.first_name)
        bal = await db.get_berries(uid)
        if bet < 10: return await message.reply("Min bet is 10🫐")
        if bal < bet: return await message.reply(f"❌ You only have {bal}🫐!")
        await db.remove_berries(uid, bet)
    emojis = ["🍒","🍋","🍊","🍇","🔔","💎","7️⃣"]
    result = [random.choice(emojis) for _ in range(3)]
    is_jackpot = len(set(result)) == 1
    text = f"🎰 <b>Slots</b>\n\n│ {' │ '.join(result)} │\n\n"
    won = 0
    if is_jackpot:
        text += "🎉 <b>JACKPOT!</b> 🎉"
        won = bet * 10 if bet > 0 else 0
    elif len(set(result)) == 2:
        text += "👏 Almost! Won 1.5x"
        won = int(bet * 1.5) if bet > 0 else 0
    else:
        text += "❌ Try again!"
        won = 0
    if bet > 0 and db:
        if won > 0:
            await db.add_berries(uid, won)
            text += f"\n\n🎉 <b>You won {won}🫐!</b>"
        else:
            text += f"\n\n😢 <b>Lost {bet}🫐</b>"
        text += f"\n💰 Balance: {await db.get_berries(uid)}🫐"
    await message.react("🎰")
    await message.reply(text)
