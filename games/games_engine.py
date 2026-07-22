import random, asyncio
from typing import Optional, Dict, List, Tuple
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.mongo import MongoDB
from utils.buttons import Buttons
from utils.helpers import Helpers

class GameEngine:
    def __init__(self, bot: Client, db: MongoDB):
        self.bot = bot
        self.db = db
        self.h = Helpers()
        self.games: Dict[str, Dict] = {}
        self.multiplayer: Dict[str, Dict] = {}
        self.quiz_qs = self._quiz_data()

    def _quiz_data(self):
        return [
            {"q": "What is the capital of France?", "a": "Paris", "opts": ["London","Paris","Berlin","Madrid"]},
            {"q": "Which planet is known as Red Planet?", "a": "Mars", "opts": ["Venus","Mars","Jupiter","Saturn"]},
            {"q": "Who wrote Romeo and Juliet?", "a": "Shakespeare", "opts": ["Dickens","Shakespeare","Austen","Hemingway"]},
            {"q": "What is the largest ocean?", "a": "Pacific", "opts": ["Atlantic","Indian","Pacific","Arctic"]},
            {"q": "What year did WW2 end?", "a": "1945", "opts": ["1943","1944","1945","1946"]},
            {"q": "Which gas do plants absorb?", "a": "CO2", "opts": ["O2","N2","CO2","H2"]},
            {"q": "What is the speed of light?", "a": "300000 km/s", "opts": ["150000","300000","500000","100000"]},
            {"q": "Which animal is King of Jungle?", "a": "Lion", "opts": ["Tiger","Lion","Elephant","Bear"]},
            {"q": "What color are emeralds?", "a": "Green", "opts": ["Red","Blue","Green","Yellow"]},
            {"q": "How many days in a year?", "a": "365", "opts": ["364","365","366","360"]},
            {"q": "What is 2+2?", "a": "4", "opts": ["3","4","5","6"]},
            {"q": "Which language runs in browser?", "a": "JavaScript", "opts": ["Python","Java","JavaScript","C++"]},
            {"q": "What does CPU stand for?", "a": "Central Processing Unit", "opts": ["Central Process Unit","Computer Personal Unit","Central Processing Unit","Core Process Unit"]},
            {"q": "Which country has most people?", "a": "India", "opts": ["China","India","USA","Indonesia"]},
            {"q": "What is the smallest country?", "a": "Vatican", "opts": ["Monaco","Vatican","San Marino","Liechtenstein"]},
        ]

    async def start_game(self, chat_id: int, user_id: int, game_type: str, username: str = "Player"):
        gid = f"{chat_id}_{game_type}_{user_id}_{random.randint(1000,9999)}"
        if game_type == "ttt":
            return self._init_ttt(gid, chat_id, user_id, username)
        elif game_type == "trivia":
            return self._init_trivia(gid, chat_id, user_id)
        elif game_type == "word":
            return self._init_word(gid, chat_id, user_id)
        elif game_type == "2048":
            return self._init_2048(gid, chat_id, user_id)
        elif game_type == "c4":
            return self._init_c4(gid, chat_id, user_id, username)
        elif game_type == "number":
            return self._init_num(gid, chat_id, user_id)
        return None

    async def handle_callback(self, client, query):
        data = query.data
        if data.startswith("ttt_"): await self._ttt_move(client, query)
        elif data.startswith("trivia_"): await self._trivia_answer(client, query)
        elif data.startswith("word_"): await self._word_guess(client, query)
        elif data.startswith("2048_"): await self._2048_move(client, query)
        elif data.startswith("c4_"): await self._c4_move(client, query)
        elif data.startswith("numguess_"): await self._num_guess(client, query)
        elif data.startswith("mp_"): await self._mp_handler(client, query)

    def _init_ttt(self, gid, chat_id, uid, uname):
        self.games[gid] = {"type":"ttt","board":[" "]*9,"turn":"X","players":{"X":uid},"scores":{"X":0,"O":0},"over":False,"winner":None,"chat_id":chat_id}
        return f"❌ <b>Tic Tac Toe</b>\n\n{uname} started!\nTap ⬜ to play.\nWaiting for opponent...", None

    async def _ttt_move(self, client, query):
        parts = query.data.split("_", 2)
        gid = parts[1]
        pos = int(parts[2])
        game = self.games.get(gid)
        if not game or game["over"]: return
        uid = query.from_user.id
        if game["players"]["X"] != uid:
            if "O" not in game["players"]: game["players"]["O"] = uid
            elif game["players"]["O"] != uid:
                await query.answer("Not your turn!", show_alert=True); return
        cp = "X" if game["players"]["X"] == uid else "O"
        if cp != game["turn"]: await query.answer("Wait!", show_alert=True); return
        if game["board"][pos] != " ": await query.answer("Taken!", show_alert=True); return
        game["board"][pos] = game["turn"]
        w = self._check_ttt(game["board"])
        if w:
            game["over"] = True; game["winner"] = w
            await self.db.inc_user(game["players"][w], "games_won")
            for p in game["players"].values(): await self.db.inc_user(p, "games_played")
            text = f"🏆 Player {w} wins!\n\n"
        elif " " not in game["board"]:
            game["over"] = True
            text = f"🤝 Draw!\n\n"
        else:
            game["turn"] = "O" if game["turn"]=="X" else "X"
            text = f"❌ Tic Tac Toe | Turn: {'❌' if game['turn']=='X' else '⭕'}\n\n"
        bd = ""
        for i in range(0,9,3):
            row = " | ".join([c if c!=" " else str(i+j+1) for j,c in enumerate(game["board"][i:i+3])])
            bd += f"`{row}`\n"
        text += bd
        short = gid.split("_",1)[1] if "_" in gid else gid
        await query.message.edit(text, reply_markup=Buttons.ttt_board(short, game["board"], game["turn"], str(game["players"]["X"]), str(game["players"].get("O",""))))
        await query.answer()

    def _check_ttt(self, b):
        for p in [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]:
            if b[p[0]]==b[p[1]]==b[p[2]]!=" ": return b[p[0]]
        return None

    def _init_trivia(self, gid, chat_id, uid):
        q = random.choice(self.quiz_qs)
        self.games[gid] = {"type":"trivia","q":q,"answered":set(),"uid":uid,"chat_id":chat_id}
        buttons = []
        opts = q["opts"][:]; random.shuffle(opts)
        for o in opts:
            buttons.append([InlineKeyboardButton(o, callback_data=f"trivia_{gid}_{o}")])
        return f"❓ <b>Trivia</b>\n\n<b>{q['q']}</b>", InlineKeyboardMarkup(buttons)

    async def _trivia_answer(self, client, query):
        parts = query.data.split("_", 2)
        gid = parts[1]; ans = parts[2]
        game = self.games.get(gid)
        if not game: return
        if query.from_user.id in game["answered"]:
            await query.answer("Already answered!", show_alert=True); return
        game["answered"].add(query.from_user.id)
        correct = game["q"]["a"]
        if ans == correct:
            game["score"] = game.get("score",0)+1
            await self.db.inc_user(query.from_user.id, "total_score", 10)
            await query.answer(f"✅ Correct! +10pts", show_alert=True)
        else:
            await query.answer(f"❌ Answer: {correct}", show_alert=True)
        text = f"❓ <b>Trivia</b>\n\n<b>{game['q']['q']}</b>\n\nCorrect: {correct}\nScore: {game.get('score',0)}"
        await query.message.edit(text, reply_markup=Buttons.back_button("menu_games"))

    def _init_word(self, gid, chat_id, uid):
        words = ["python","telegram","music","game","bot","code","zenii","beatz","stream","player"]
        word = random.choice(words)
        scrambled = list(word); random.shuffle(scrambled)
        scrambled = "".join(scrambled)
        self.games[gid] = {"type":"word","word":word,"scrambled":scrambled,"hints":3,"uid":uid,"chat_id":chat_id}
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("💡 Hint", callback_data=f"word_hint_{gid}")],
            [InlineKeyboardButton("◀️ Back", callback_data="menu_games")]
        ])
        return f"🧩 <b>Word Puzzle</b>\n\nUnscramble: <code>{scrambled}</code>\n\nType answer!", btns

    async def _word_guess(self, client, query):
        parts = query.data.split("_", 2)
        gid = parts[2]; game = self.games.get(gid)
        if not game: return
        if game["hints"] > 0:
            game["hints"] -= 1
            hint = game["word"][:len(game["word"])-game["hints"]]
            await query.answer(f"💡 Hint: {hint}", show_alert=True)

    def _init_2048(self, gid, chat_id, uid):
        board = [[0]*4 for _ in range(4)]
        self._add_tile(board); self._add_tile(board)
        self.games[gid] = {"type":"2048","board":board,"score":0,"uid":uid,"chat_id":chat_id,"over":False}
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬆️", callback_data=f"2048_up_{gid}"),
             InlineKeyboardButton("⬇️", callback_data=f"2048_down_{gid}")],
            [InlineKeyboardButton("⬅️", callback_data=f"2048_left_{gid}"),
             InlineKeyboardButton("➡️", callback_data=f"2048_right_{gid}")],
            [InlineKeyboardButton("🔄 New", callback_data="game_2048"),
             InlineKeyboardButton("◀️ Back", callback_data="menu_games")]
        ])
        return self._show_2048(board), btns

    def _show_2048(self, board):
        text = f"🎲 <b>2048</b>\n\n"
        for row in board:
            text += "`|" + "|".join(f"{str(c if c else '·'):>4}" for c in row) + "|`\n"
        return text

    def _add_tile(self, board):
        empty = [(i,j) for i in range(4) for j in range(4) if board[i][j]==0]
        if empty:
            i,j = random.choice(empty)
            board[i][j] = 2 if random.random()<0.9 else 4

    def _slide(self, row):
        new = [x for x in row if x]
        sc = 0
        for i in range(len(new)-1):
            if new[i]==new[i+1]:
                new[i]*=2; sc+=new[i]; new[i+1]=0
        new = [x for x in new if x]
        while len(new)<4: new.append(0)
        return new, sc

    async def _2048_move(self, client, query):
        parts = query.data.split("_", 2)
        direction = parts[1]; gid = parts[2]
        game = self.games.get(gid)
        if not game or game["over"]: return
        board = game["board"]; score = 0; moved = False
        if direction in ("left","right"):
            for i in range(4):
                row = board[i][:]
                if direction=="right": row.reverse()
                nr, s = self._slide(row)
                score += s
                if direction=="right": nr.reverse()
                if nr != board[i]: moved = True
                board[i] = nr
        else:
            for j in range(4):
                col = [board[i][j] for i in range(4)]
                if direction=="down": col.reverse()
                nc, s = self._slide(col); score += s
                if direction=="down": nc.reverse()
                for i in range(4):
                    if nc[i]!=board[i][j]: moved = True
                    board[i][j] = nc[i]
        game["score"] += score
        if moved:
            self._add_tile(board)
            if all(board[i][j] for i in range(4) for j in range(4)):
                game["over"] = True
                await self.db.inc_user(query.from_user.id, "total_score", game["score"])
        text = self._show_2048(board)
        if game["over"]: text += "\n💀 Game Over!"
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬆️",callback_data=f"2048_up_{gid}"),
             InlineKeyboardButton("⬇️",callback_data=f"2048_down_{gid}")],
            [InlineKeyboardButton("⬅️",callback_data=f"2048_left_{gid}"),
             InlineKeyboardButton("➡️",callback_data=f"2048_right_{gid}")],
            [InlineKeyboardButton("🔄 New",callback_data="game_2048"),
             InlineKeyboardButton("◀️ Back",callback_data="menu_games")]
        ])
        await query.message.edit(text, reply_markup=btns)
        await query.answer()

    def _init_c4(self, gid, chat_id, uid, uname):
        self.games[gid] = {"type":"c4","board":[[" "]*7 for _ in range(6)],"turn":"🔴","players":{"🔴":uid},"chat_id":chat_id,"over":False}
        return f"🏓 <b>Connect 4</b>\n\n{uname} started! Waiting for opponent...", None

    async def _c4_move(self, client, query):
        parts = query.data.split("_", 2)
        gid = parts[1]; col = int(parts[2])
        game = self.games.get(gid)
        if not game: return
        if "🟡" not in game["players"]:
            game["players"]["🟡"] = query.from_user.id
        if game["players"][game["turn"]] != query.from_user.id:
            await query.answer("Not your turn!", show_alert=True); return
        board = game["board"]
        placed = False
        for row in range(5,-1,-1):
            if board[row][col] == " ":
                board[row][col] = "🔴" if game["turn"]=="🔴" else "🟡"
                placed = True; break
        if not placed: await query.answer("Full!", show_alert=True); return
        if self._check_c4(board):
            game["over"] = True
            text = f"🏆 {game['turn']} wins!\n"
        elif all(board[0][c]!=" " for c in range(7)):
            game["over"] = True
            text = "🤝 Draw!\n"
        else:
            game["turn"] = "🟡" if game["turn"]=="🔴" else "🔴"
            text = f"🏓 Connect 4 | Turn: {game['turn']}\n"
        for r in board: text += "│" + "│".join(r) + "│\n"
        text += " 0 1 2 3 4 5 6"
        btns = [[InlineKeyboardButton(f"⬇️", callback_data=f"c4_{gid}_{c}") for c in range(7) if not game["over"]]]
        btns.append([InlineKeyboardButton("🔄 New", callback_data="game_c4"), InlineKeyboardButton("◀️ Back", callback_data="menu_games")])
        await query.message.edit(text, reply_markup=InlineKeyboardMarkup(btns))
        await query.answer()

    def _check_c4(self, board):
        for r in range(6):
            for c in range(7):
                if board[r][c]==" ": continue
                p = board[r][c]
                if c+3<7 and all(board[r][c+i]==p for i in range(4)): return True
                if r+3<6 and all(board[r+i][c]==p for i in range(4)): return True
                if r+3<6 and c+3<7 and all(board[r+i][c+i]==p for i in range(4)): return True
                if r-3>=0 and c+3<7 and all(board[r-i][c+i]==p for i in range(4)): return True
        return False

    def _init_num(self, gid, chat_id, uid):
        num = random.randint(1,100)
        self.games[gid] = {"type":"number","number":num,"attempts":0,"uid":uid,"chat_id":chat_id,"min":1,"max":100}
        return f"🎯 <b>Number Guess</b>\n\nGuess 1-100!", Buttons.back_button("menu_games")

    async def _num_guess(self, client, query):
        await query.answer("Use /number <guess> to play!")

    async def _mp_handler(self, client, query):
        mp_type = query.data.split("_")[1]
        await query.answer(f"Multiplayer {mp_type} starting...")
        await query.message.edit(
            f"🎮 <b>Multiplayer {mp_type.upper()}</b>\n\n"
            f"Challenge a friend by replying to their message with:\n"
            f"<code>/challenge {mp_type}</code>\n\n"
            f"Coming soon with full 2-player matchmaking!",
            reply_markup=Buttons.back_button("menu_games")
        )

    async def get_leaderboard(self):
        top = await self.db.get_top_users("total_score", 15)
        text = "🏆 <b>Global Leaderboard</b>\n\n"
        for i, u in enumerate(top, 1):
            name = u.get("name", f"User{u['user_id']}")
            badge = "👑" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
            text += f"{badge} <b>{name}</b> | {u['total_score']}pts | {u['games_won']}wins\n"
        return text
