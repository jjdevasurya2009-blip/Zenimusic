from pyrogram import Client, filters, emoji
from pyrogram.types import Message, Dice
from config import Config
from utils.buttons import Buttons
from utils.helpers import Helpers

h = Helpers()

@Client.on_message(filters.command("start") & filters.private)
async def start_pm(client: Client, message: Message):
    user = message.from_user
    cfg = await client.bot_instance.db.get_bot_config()
    await client.bot_instance.db.register_user(user.id, user.first_name)
    await message.react(emoji=emoji.MUSICAL_NOTE)
    text = (
        f"✧ <b>ZENII X MUSIC</b> ✧\n\n"
        f"✨ Hey {user.first_name}!\n"
        f"Advanced VC Music Bot with built-in games!\n\n"
        f"🎵 <b>Music</b>\n"
        f"• /play - Play songs\n"
        f"• /vplay - Play videos\n"
        f"• /radio - Radio stations\n"
        f"• /live - Live streams\n\n"
        f"🎮 <b>Games</b>\n"
        f"• /game - Game menu\n"
        f"• Tic Tac Toe, Connect 4, 2048, Quiz\n\n"
        f"⚡ <b>Premium</b>\n"
        f"• Higher queue limits\n"
        f"• More playlist space\n"
        f"• Priority support\n\n"
        f"📌 Add me to groups: /help for commands"
    )
    img = cfg.get("start_img", "")
    if img:
        await message.reply_photo(img, caption=text, reply_markup=Buttons.start_buttons(
            cfg.get("support_url", Config.SUPPORT_URL),
            cfg.get("updates_url", Config.UPDATES_URL)
        ))
    else:
        await message.reply(text, reply_markup=Buttons.start_buttons(
            cfg.get("support_url", Config.SUPPORT_URL),
            cfg.get("updates_url", Config.UPDATES_URL)
        ))

@Client.on_message(filters.command("start") & filters.group)
async def start_group(client: Client, message: Message):
    await message.react(emoji=emoji.MUSICAL_NOTE)
    await message.reply(
        f"✧ <b>ZENII X MUSIC</b> ✧\n\n"
        f"🎵 Ready to play!\n"
        f"• /play <song> - Play music\n"
        f"• /vplay <song> - Play video\n"
        f"• /game - Play games\n"
        f"• /earn - Earn 🫐 berries\n"
        f"• /wish - Pull waifus 🌸\n"
        f"• /rob - Rob someone\n"
        f"• /marry - Find love 💕\n"
        f"• /bank - Deposit berries\n"
        f"• /lottery - Win big 🎰\n"
        f"• /radio - Radio\n\n"
        f"Join @zenii_updates for updates!"
    )

@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.react(emoji=emoji.INFORMATION)
    text = (
        "✧ <b>ZENII X MUSIC — HELP</b> ✧\n\n"
        "<b>🎵 Music</b>\n"
        "/play <song> - Play audio\n"
        "/vplay <song> - Play video\n"
        "/radio <station> - Radio (jazz, rock, lofi...)\n"
        "/live <url> - Live stream\n"
        "/pause - Pause\n"
        "/resume - Resume\n"
        "/skip - Skip\n"
        "/stop - Stop & leave\n"
        "/queue - Show queue\n"
        "/shuffle - Shuffle queue\n"
        "/loop - Toggle loop\n"
        "/volume <1-200> - Volume\n"
        "/seek <s> - Seek position\n"
        "/current - Now playing\n"
        "/forceplay <song> - Force play (admin)\n"
        "/lyrics <song> - Get lyrics\n"
        "/song <name> - Download audio\n"
        "/video <name> - Download video\n\n"
        "<b>🎮 Games</b>\n"
        "/game - Games menu\n"
        "/ttt - Tic Tac Toe\n"
        "/trivia - Trivia Quiz\n"
        "/word - Word Puzzle\n"
        "/2048 - Play 2048\n"
        "/connect4 - Connect 4\n"
        "/number - Guess number\n"
        "/leaderboard - Top players\n\n"
        "<b>🎲 Economy & Multiplayer</b>\n"
        "/earn - Earn berries\n"
        "/daily - Daily reward\n"
        "/shop - Buy items\n"
        "/inv - Your inventory\n"
        "/use <item> - Use an item\n"
        "/bank - Check bank balance\n"
        "/deposit <amt> - Deposit berries\n"
        "/withdraw <amt> - Withdraw berries\n"
        "/lottery - Lottery info\n"
        "/buyticket <n> - Buy lottery tickets\n"
        "/bet <amt> - 50/50 gamble\n"
        "/slots <amt> - Slot machine\n"
        "/dice <sides> <amt> - Dice game\n"
        "/flip <amt> - Coin flip\n"
        "/dart <amt> - Dart throw\n"
        "/wish - Pull gacha characters\n"
        "/collection - Your character collection\n"
        "/waifus - Your caught waifus\n"
        "/fav <name> - Set favorite character\n"
        "/rob - Rob someone\n"
        "/kill - Kill someone\n"
        "/revive - Revive someone\n"
        "/duel - Duel someone\n"
        "/gift <amt> - Gift berries\n"
        "/marry - Propose marriage\n"
        "/divorce - Divorce\n"
        "/spouse - Show spouse\n"
        "/profile - Your profile\n"
        "/level - XP & level stats\n"
        "/achievements - Badges & achievements\n"
        "/rich - Leaderboard\n\n"
        "<b>🎨 Fonts & Quotes</b>\n"
        "/smallcaps <text> - Small caps font\n"
        "/fancy <text> - Fancy script font\n"
        "/fraktur <text> - Gothic fraktur font\n"
        "/boldfont <text> - Bold sans font\n"
        "/monofont <text> - Monospace font\n"
        "/doublestruck <text> - Double struck font\n"
        "/fontlist - Show all font styles\n"
        "/quote (reply) - Quote a message\n"
        "/quotereply (reply) - Reply with quote\n"
        "/qm <text> - Create quote from text\n\n"
        "<b>⚙️ Group Management</b>\n"
        "/ban <user> - Ban user\n"
        "/unban <user> - Unban user\n"
        "/mute <user> - Mute user\n"
        "/unmute <user> - Unmute user\n"
        "/pin <msg> - Pin message\n"
        "/purge <n> - Delete messages\n"
        "/warn <user> - Warn user\n"
        "/tagall - Mention everyone\n"
        "/antispam on/off - Auto moderation\n"
        "/setwelcome <msg> - Custom welcome\n"
        "/setgoodbye <msg> - Custom goodbye\n"
        "/settings - Chat settings\n\n"
        "<b>🎵 Music Control</b>\n"
        "/play <song> - Play music\n"
        "/vplay <song> - Play video\n"
        "/radio <station> - Radio stream\n"
        "/live <url> - Live stream\n"
        "/voteskip - Vote to skip song\n"
        "/forceskip - Force skip (auth)\n"
        "/clearqueue - Clear the queue\n"
        "/move <from> <to> - Reorder queue\n"
        "/playlist - Manage playlists\n"
        "/importpl <url> - Import playlist\n\n"
        "<b>🔐 Premium</b>\n"
        "/premium - Check status\n\n"
        "<b>ℹ️</b> /ping - Ping\n/id - IDs\n/stats - Bot stats"
    )
    await message.reply(text)

@Client.on_message(filters.command("premium"))
async def premium_check(client: Client, message: Message):
    uid = message.from_user.id
    is_prem = await client.bot_instance.db.is_premium(uid)
    if is_prem:
        u = await client.bot_instance.db.get_user(uid)
        expiry = u.get("premium_expiry", "N/A")
        text = (
            "⭐ <b>Premium Active</b> ⭐\n\n"
            f"✅ You are a premium user!\n"
            f"📅 Expiry: {expiry}\n\n"
            f"<b>Benefits:</b>\n"
            f"• Queue limit: {Config.PREMIUM_MAX_QUEUE} songs\n"
            f"• Playlist limit: {Config.PREMIUM_PLAYLIST_LIMIT} songs\n"
            f"• Priority queue\n"
            f"• Premium badge"
        )
    else:
        text = (
            "⭐ <b>Premium</b>\n\n"
            "You are not a premium user.\n"
            "Contact owner to get premium access!\n\n"
            "<b>Benefits:</b>\n"
            f"• Queue limit: {Config.PREMIUM_MAX_QUEUE} (free: {Config.MAX_QUEUE})\n"
            f"• Playlist limit: {Config.PREMIUM_PLAYLIST_LIMIT} (free: {Config.DEFAULT_PLAYLIST_LIMIT})\n"
            "• Priority support\n"
            "• Priority queue position"
        )
    await message.reply(text)
