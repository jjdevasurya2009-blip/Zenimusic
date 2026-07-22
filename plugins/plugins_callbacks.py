from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import Config
from utils.buttons import Buttons
from utils.helpers import Helpers

h = Helpers()

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    uid = query.from_user.id
    bot = client.bot_instance
    db = bot.db

    if data == "close":
        await query.message.delete()
        return await query.answer()

    if data.startswith("menu_"):
        menu = data.split("_")[1]
        if menu == "music":
            text = "🎵 <b>Music</b>\n\n/play <song> - Play\n/vplay <song> - Video\n/radio - Radio\n/live - Live\n/pause, /resume, /skip, /stop"
            await query.message.edit(text, reply_markup=Buttons.vc_buttons())
        elif menu == "vplay":
            text = "📺 <b>Video Play</b>\n\nUse /vplay <song or URL> to play video in VC!"
            await query.message.edit(text, reply_markup=Buttons.back_button("menu_music"))
        elif menu == "radio":
            stations = "\n".join([f"• /radio {s}" for s in bot.music_player.radio_stations])
            text = f"📻 <b>Radio</b>\n\n{stations}"
            await query.message.edit(text, reply_markup=Buttons.back_button("menu_music"))
        elif menu == "live":
            text = "🔴 <b>Live Stream</b>\n\nUse /live <YouTube live URL> to stream live!"
            await query.message.edit(text, reply_markup=Buttons.back_button("menu_music"))
        elif menu == "games":
            text = "🎮 <b>Games</b>\n\nChoose a game!"
            await query.message.edit(text, reply_markup=Buttons.games_menu())
        elif menu == "multiplayer":
            text = "🤼 <b>Multiplayer</b>\n\nPlay with friends!"
            await query.message.edit(text, reply_markup=Buttons.multiplayer_menu())
        elif menu == "queue":
            text = "📋 Queue - Use /queue"
            await query.message.edit(text, reply_markup=Buttons.back_button("back_start"))
        elif menu == "settings":
            cfg = await db.get_chat_settings(query.message.chat.id)
            text = f"⚙️ <b>Settings</b>\n\nVol: {cfg.get('volume',100)}%\nLoop: {'ON' if cfg.get('loop') else 'OFF'}"
            await query.message.edit(text, reply_markup=Buttons.settings_buttons())
        elif menu == "help":
            text = "❓ <b>Help</b>\n\n/play, /vplay, /radio, /live\n/game, /ttt, /trivia, /2048\n/help for full list"
            await query.message.edit(text, reply_markup=Buttons.back_button("back_start"))
        await query.answer()

    elif data.startswith("ctrl_"):
        action = data.split("_")[1]
        cid = query.message.chat.id
        mp = bot.music_player
        if action == "pause": await mp.pause(cid); await query.answer("⏸ Paused")
        elif action == "resume": await mp.resume(cid); await query.answer("▶️ Resumed")
        elif action == "skip": await mp.skip(cid); await query.answer("⏭ Skipped")
        elif action == "stop": await mp.stop(cid); await query.answer(Helpers.interactive_leave(), show_alert=True)
        elif action == "shuffle": await mp.shuffle(cid); await query.answer("🔀 Shuffled")
        elif action == "loop":
            cur = mp.loop.get(cid, False)
            mp.set_loop(cid, not cur)
            await query.answer(f"🔁 Loop: {'ON' if not cur else 'OFF'}")
        elif action == "queue":
            q = mp.get_queue(cid)
            text = "📋 Queue:\n" + "\n".join([f"{i}. {s['title'][:30]}" for i,s in enumerate(q[:10],1)]) if q else "Empty"
            await query.answer(text[:200])
        elif action == "vol_up":
            vol = mp.volumes.get(cid, 100)
            mp.volumes[cid] = min(200, vol+10)
            await query.answer(f"🔊 Volume: {mp.volumes[cid]}%")
        elif action == "vol_down":
            vol = mp.volumes.get(cid, 100)
            mp.volumes[cid] = max(0, vol-10)
            await query.answer(f"🔉 Volume: {mp.volumes[cid]}%")
        elif action == "clear":
            mp.queues[cid] = []
            await query.answer("🗑 Queue cleared")

    elif data.startswith("game_"):
        game = data.split("_")[1]
        cid = query.message.chat.id
        eng = bot.game_engine
        if game == "ttt":
            r, _ = await eng.start_game(cid, uid, "ttt", query.from_user.first_name)
            await query.message.edit(r, reply_markup=Buttons.ttt_board(f"{cid}_ttt_{uid}_{id(query)}", [" "]*9, "X", str(uid), ""))
        elif game == "trivia":
            r, btns = await eng.start_game(cid, uid, "trivia")
            await query.message.edit(r, reply_markup=btns)
        elif game == "word":
            r, btns = await eng.start_game(cid, uid, "word")
            await query.message.edit(r, reply_markup=btns)
        elif game == "2048":
            r, btns = await eng.start_game(cid, uid, "2048")
            await query.message.edit(r, reply_markup=btns)
        elif game == "c4":
            r, _ = await eng.start_game(cid, uid, "c4", query.from_user.first_name)
            await query.message.edit(r)
        elif game == "number":
            r, btns = await eng.start_game(cid, uid, "number")
            await query.message.edit(r, reply_markup=btns)
        elif game == "multiplayer":
            await query.message.edit("🤼 <b>Multiplayer</b>", reply_markup=Buttons.multiplayer_menu())
        elif game == "leaderboard":
            text = await eng.get_leaderboard()
            await query.message.edit(text, reply_markup=Buttons.back_button("menu_games"))
        elif game == "rps":
            import random as rnd
            player = "rock"; bot_choice = rnd.choice(["rock","paper","scissors"])
            em = {"rock":"🪨","paper":"📄","scissors":"✂️"}
            beats = {"rock":"scissors","scissors":"paper","paper":"rock"}
            result = "🤝 Draw!" if player==bot_choice else ("🎉 You win!" if beats[player]==bot_choice else "🤖 Bot wins!")
            await query.message.edit(
                f"🪨 <b>RPS</b>\n\nYou: {em[player]} {player.title()}\nBot: {em[bot_choice]} {bot_choice.title()}\n\n<b>{result}</b>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Again", callback_data="game_rps")]])
            )
        await query.answer()

    elif data.startswith("ttt_") or data.startswith("trivia_") or data.startswith("word_") or data.startswith("2048_") or data.startswith("c4_"):
        await bot.game_engine.handle_callback(client, query)

    elif data.startswith("mp_"):
        mp_type = data.split("_")[1]
        await query.answer(f"Multiplayer {mp_type}!")
        await query.message.edit(
            f"🤼 <b>Multiplayer {mp_type.upper()}</b>\n\nReply to someone with: <code>/challenge {mp_type}</code>\nComing soon!",
            reply_markup=Buttons.back_button("menu_games")
        )

    elif data == "back_start":
        cfg = await db.get_bot_config()
        text = f"✧ <b>ZENII X MUSIC</b> ✧\n\n🎵 /play - Music\n🎮 /game - Games\n❓ /help"
        await query.message.edit(text, reply_markup=Buttons.start_buttons(
            cfg.get("support_url","https://t.me/zenii_support"),
            cfg.get("updates_url","https://t.me/zenii_updates")
        ))
        await query.answer()

    elif data.startswith("set_"):
        setting = data.split("_")[1]
        await query.answer(f"⚙️ {setting}")
        await query.message.edit(f"⚙️ <b>{setting.title()}</b>\n\nUse /settings in group to configure.", reply_markup=Buttons.back_button("menu_settings"))

    elif data.startswith("qpage_"):
        parts = data.split("_")
        await query.answer(f"Page {int(parts[1])+1}")

    elif data == "admin_panel":
        text = f"⚙️ <b>Admin Panel</b>\nCalls: {bot.voice_handler.call_count}"
        await query.message.edit(text, reply_markup=Buttons.admin_panel())
        await query.answer()

    elif data == "admin_config":
        cfg = await db.get_bot_config()
        text = "📝 <b>Bot Config</b>\n\n"
        text += f"Support: {cfg.get('support_url','?')}\n"
        text += f"Updates: {cfg.get('updates_url','?')}\n"
        text += f"Reaction: {cfg.get('reaction_emoji',Config.REACTION_EMOJI)}\n"
        text += f"Playlist Limit: {cfg.get('playlist_limit',Config.DEFAULT_PLAYLIST_LIMIT)}\n"
        text += f"Premium Limit: {cfg.get('premium_playlist_limit',Config.PREMIUM_PLAYLIST_LIMIT)}"
        await query.message.edit(text, reply_markup=Buttons.config_panel())
        await query.answer()

    elif data.startswith("cfg_"):
        key = data.split("_")[1]
        await query.answer(f"Configure {key}")
        await query.message.edit(
            f"📝 <b>Set {key.title()}</b>\n\n"
            f"Send the new value for {key} in this chat.\n"
            f"Example: <code>/setcfg {key} new_value</code>",
            reply_markup=Buttons.back_button("admin_config")
        )

    elif data == "admin_coowners":
        cos = await db.get_co_owners()
        text = "👥 <b>Co-Owners</b>\n\n"
        if cos:
            for c in cos:
                text += f"• {c['user_id']}\n"
        else:
            text += "None\n"
        text += "\nUse /addco <id> or /removeco <id>"
        await query.message.edit(text, reply_markup=Buttons.back_button("admin_panel"))
        await query.answer()

    elif data == "admin_auth":
        aus = await db.get_all_auth_users()
        text = "🔐 <b>Auth Users</b>\n\n"
        if aus:
            for au in aus:
                name = au.get("name", str(au["user_id"]))[:20]
                perms = au.get("permissions", {})
                text += f"• {name} ({au['user_id']}) - {sum(1 for v in perms.values() if v)}cmds\n"
        else:
            text += "None\n"
        text += "\nUse /addauth <id> or /removeauth <id>"
        await query.message.edit(text, reply_markup=Buttons.back_button("admin_panel"))
        await query.answer()

    elif data == "admin_premium":
        prems = await db.db.users.find({"is_premium": True}).to_list(length=None)
        text = "⭐ <b>Premium Users</b>\n\n"
        if prems:
            for p in prems:
                text += f"• {p.get('name','?')} ({p['user_id']}) - Exp: {p.get('premium_expiry','?')}\n"
        else:
            text += "None\n"
        text += "\nUse /premium add <id> <days>"
        await query.message.edit(text, reply_markup=Buttons.back_button("admin_panel"))
        await query.answer()

    elif data == "admin_blacklist":
        bl = await db.get_blacklist()
        text = "🚫 <b>Blacklisted Chats</b>\n\n"
        if bl:
            for b in bl:
                text += f"• {b['chat_id']}\n"
        else:
            text += "None\n"
        text += "\nUse /blacklist <chat_id> or /whitelist <chat_id>"
        await query.message.edit(text, reply_markup=Buttons.back_button("admin_panel"))
        await query.answer()

    elif data == "admin_calls":
        count = bot.voice_handler.call_count
        text = f"📞 <b>Active Calls</b>\n\nCurrently: <b>{count}</b>\n"
        if bot.voice_handler.active_calls:
            text += "\nActive chats:\n"
            for cid in bot.voice_handler.active_calls:
                text += f"• {cid}\n"
        await query.message.edit(text, reply_markup=Buttons.back_button("admin_panel"))
        await query.answer()

    elif data == "admin_logs":
        logs = await db.get_logs(20)
        text = "📜 <b>Recent Logs</b>\n\n"
        for l in logs:
            t = l.get("type","?")
            d = str(l.get("data",{}))[:50]
            text += f"• [{t}] {d}\n"
        await query.message.edit(text, reply_markup=Buttons.close_button())
        await query.answer()

    elif data.startswith("play_"):
        url = data.split("_",1)[1]
        await query.answer("▶️ Playing...")
        await bot.music_player.play_song(query.message.chat.id, url, uid)

    elif data.startswith("dl_"):
        url = data.split("_",2)[2] if len(data.split("_"))>2 else ""
        await query.answer("📥 Download coming soon!")

    elif data.startswith("auth_view_"):
        parts = data.split("_")
        auid = int(parts[2])
        page = parts[3] if len(parts)>3 else 0
        au = await db.get_auth_user(auid)
        if au:
            perms = au.get("permissions", {})
            text = f"🔐 <b>Auth User: {auid}</b>\n\nPermissions:\n"
            for cmd, allowed in perms.items():
                text += f"{'✅' if allowed else '❌'} /{cmd}\n"
            text += "\nUse /setauth <id> <cmd> <on/off>"
        else:
            text = "Not found"
        await query.message.edit(text, reply_markup=Buttons.back_button("admin_panel"))
        await query.answer()

    elif data.startswith("noop"):
        await query.answer()

    else:
        await query.answer("Unknown action")
