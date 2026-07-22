from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class Buttons:
    @staticmethod
    def start_buttons(support="https://t.me/zenii_support", updates="https://t.me/zenii_updates"):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎵 Play Music", callback_data="menu_music"),
             InlineKeyboardButton("🎮 Games", callback_data="menu_games")],
            [InlineKeyboardButton("🫐 Earn Berries", callback_data="menu_earn"),
             InlineKeyboardButton("🛒 Shop", callback_data="menu_shop")],
            [InlineKeyboardButton("📋 Queue", callback_data="menu_queue"),
             InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
            [InlineKeyboardButton("❓ Help", callback_data="menu_help"),
             InlineKeyboardButton("📢 Channel", url=updates)],
            [InlineKeyboardButton("💬 Support", url=support),
             InlineKeyboardButton("➕ Add to Group", url="https://t.me/zenii_X_music_bot?startgroup=true")]
        ])

    @staticmethod
    def music_controls():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⏮", callback_data="ctrl_prev"),
             InlineKeyboardButton("⏸", callback_data="ctrl_pause"),
             InlineKeyboardButton("⏭", callback_data="ctrl_skip"),
             InlineKeyboardButton("⏹", callback_data="ctrl_stop")],
            [InlineKeyboardButton("🔀 Shuffle", callback_data="ctrl_shuffle"),
             InlineKeyboardButton("🔁 Loop", callback_data="ctrl_loop"),
             InlineKeyboardButton("📋 Queue", callback_data="ctrl_queue")],
            [InlineKeyboardButton("🔉 Vol -", callback_data="ctrl_vol_down"),
             InlineKeyboardButton("🔊 Vol +", callback_data="ctrl_vol_up"),
             InlineKeyboardButton("🎛 Settings", callback_data="ctrl_settings")]
        ])

    @staticmethod
    def vc_buttons():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📺 vPlay", callback_data="menu_vplay"),
             InlineKeyboardButton("📻 Radio", callback_data="menu_radio")],
            [InlineKeyboardButton("🔴 Live Stream", callback_data="menu_live"),
             InlineKeyboardButton("◀️ Back", callback_data="back_start")]
        ])

    @staticmethod
    def games_menu():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Tic Tac Toe", callback_data="game_ttt")],
            [InlineKeyboardButton("🏓 Connect 4", callback_data="game_c4")],
            [InlineKeyboardButton("🎲 2048", callback_data="game_2048")],
            [InlineKeyboardButton("🧩 Word Puzzle", callback_data="game_word")],
            [InlineKeyboardButton("❓ Trivia Quiz", callback_data="game_trivia")],
            [InlineKeyboardButton("🎯 Number Guess", callback_data="game_number")],
            [InlineKeyboardButton("🤼 Multiplayer", callback_data="game_multiplayer")],
            [InlineKeyboardButton("📊 Leaderboard", callback_data="game_leaderboard")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_start")]
        ])

    @staticmethod
    def multiplayer_menu():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Tic Tac Toe (2P)", callback_data="mp_ttt")],
            [InlineKeyboardButton("🏓 Connect 4 (2P)", callback_data="mp_c4")],
            [InlineKeyboardButton("🎯 Battle Quiz", callback_data="mp_quiz")],
            [InlineKeyboardButton("🪨 RPS Battle", callback_data="game_rps")],
            [InlineKeyboardButton("◀️ Back", callback_data="menu_games")]
        ])

    @staticmethod
    def settings_buttons():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎵 Volume", callback_data="set_volume"),
             InlineKeyboardButton("🌐 Language", callback_data="set_lang")],
            [InlineKeyboardButton("🔊 Audio Quality", callback_data="set_quality"),
             InlineKeyboardButton("👋 Auto Leave", callback_data="set_autoleave")],
            [InlineKeyboardButton("🔁 Auto Play", callback_data="set_autoplay"),
             InlineKeyboardButton("🌙 Night Mode", callback_data="set_nightmode")],
            [InlineKeyboardButton("📋 Queue Limit", callback_data="set_queuelimit")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_start")]
        ])

    @staticmethod
    def admin_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("👥 Manage Co-Owners", callback_data="admin_coowners")],
            [InlineKeyboardButton("🔐 Auth Users", callback_data="admin_auth")],
            [InlineKeyboardButton("⭐ Premium Users", callback_data="admin_premium")],
            [InlineKeyboardButton("🚫 Blacklist", callback_data="admin_blacklist")],
            [InlineKeyboardButton("📊 Active Calls", callback_data="admin_calls")],
            [InlineKeyboardButton("📝 Bot Config", callback_data="admin_config")],
            [InlineKeyboardButton("📜 Logs", callback_data="admin_logs")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_start")]
        ])

    @staticmethod
    def config_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Support URL", callback_data="cfg_support")],
            [InlineKeyboardButton("📢 Updates URL", callback_data="cfg_updates")],
            [InlineKeyboardButton("🖼 Start Image", callback_data="cfg_startimg")],
            [InlineKeyboardButton("🎭 Reaction Emoji", callback_data="cfg_emoji")],
            [InlineKeyboardButton("📋 Playlist Limit", callback_data="cfg_playlist")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
        ])

    @staticmethod
    def close_button():
        return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]])

    @staticmethod
    def back_button(cb="back_start"):
        return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data=cb)]])

    @staticmethod
    def queue_buttons(page, total, chat_id):
        buttons = []
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"qpage_{page-1}_{chat_id}"))
        nav.append(InlineKeyboardButton(f"{page+1}/{total}", callback_data="noop"))
        if page < total-1:
            nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"qpage_{page+1}_{chat_id}"))
        if nav: buttons.append(nav)
        buttons.append([InlineKeyboardButton("🔀 Shuffle", callback_data="ctrl_shuffle"),
                        InlineKeyboardButton("🗑 Clear", callback_data="ctrl_clear")])
        buttons.append([InlineKeyboardButton("◀️ Back", callback_data="back_start")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def play_buttons():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💾 Download Audio", callback_data="dl_audio"),
             InlineKeyboardButton("📥 Download Video", callback_data="dl_video")],
            [InlineKeyboardButton("🔗 Share", switch_inline_query="")]
        ])

    @staticmethod
    def auth_user_buttons(users, page=0):
        buttons = []
        for u in users[page*5:(page+1)*5]:
            name = u.get("name", str(u["user_id"]))[:20]
            buttons.append([InlineKeyboardButton(f"👤 {name}", callback_data=f"auth_view_{u['user_id']}_{page}")])
        nav = []
        if page > 0: nav.append(InlineKeyboardButton("◀️", callback_data=f"auth_page_{page-1}"))
        nav.append(InlineKeyboardButton(f"{page+1}/{(len(users)-1)//5+1}", callback_data="noop"))
        if (page+1)*5 < len(users): nav.append(InlineKeyboardButton("▶️", callback_data=f"auth_page_{page+1}"))
        if nav: buttons.append(nav)
        buttons.append([InlineKeyboardButton("➕ Add User", callback_data="auth_add")])
        buttons.append([InlineKeyboardButton("◀️ Back", callback_data="admin_panel")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def premium_user_buttons(users, page=0):
        buttons = []
        for u in users[page*5:(page+1)*5]:
            name = u.get("name", str(u["user_id"]))[:20]
            buttons.append([InlineKeyboardButton(f"⭐ {name}", callback_data=f"prem_view_{u['user_id']}_{page}")])
        nav = []
        if page > 0: nav.append(InlineKeyboardButton("◀️", callback_data=f"prem_page_{page-1}"))
        nav.append(InlineKeyboardButton(f"{page+1}/{(len(users)-1)//5+1}", callback_data="noop"))
        if (page+1)*5 < len(users): nav.append(InlineKeyboardButton("▶️", callback_data=f"prem_page_{page+1}"))
        if nav: buttons.append(nav)
        buttons.append([InlineKeyboardButton("➕ Add Premium", callback_data="prem_add")])
        buttons.append([InlineKeyboardButton("◀️ Back", callback_data="admin_panel")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def ttt_board(gid, board, turn, px, po):
        buttons = []
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                idx = i+j
                v = board[idx]
                if v == "X": text = "❌"
                elif v == "O": text = "⭕"
                else: text = "⬜"
                row.append(InlineKeyboardButton(text, callback_data=f"ttt_{gid}_{idx}"))
            buttons.append(row)
        buttons.append([InlineKeyboardButton("🔄 New", callback_data="game_ttt"),
                        InlineKeyboardButton("◀️ Back", callback_data="menu_games")])
        return InlineKeyboardMarkup(buttons)
