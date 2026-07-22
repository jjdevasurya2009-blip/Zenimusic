import motor.motor_asyncio
from datetime import datetime, timedelta
from config import Config

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client["ZeniiXMusic"]
        await self.db.command("ping")

    async def close(self):
        if self.client:
            self.client.close()

    # ---- Users ----
    async def register_user(self, user_id, name, referrer=0):
        data = {"user_id": user_id, "name": name, "games_played": 0, "games_won": 0,
                "total_score": 0, "is_premium": False, "premium_expiry": None,
                "banned": False, "ban_reason": "", "joined_at": datetime.now(),
                "songs_played": 0, "playlists": {},
                "berries": 0, "total_earned": 0, "rob_success": 0, "rob_fail": 0,
                "kills": 0, "deaths": 0, "revives": 0, "alive": True,
                "inventory": {}, "referrals": 0, "referrer": referrer,
                "earn_cooldown": None,
                "married_to": None, "married_since": None,
                "duel_wins": 0, "duel_losses": 0,
                "daily_streak": 0, "last_daily": None,
                "bank": 0, "last_interest": None,
                "xp": 0, "level": 1, "total_messages": 0,
                "characters": {}, "favorite_char": None, "wishes": 0,
                "monster_kills": 0, "monster_damage": 0,
                "lottery_tickets": 0, "lottery_wins": 0,
                "buff_expiry": None, "buff_type": None,
                "achievements": []}
        await self.db.users.update_one({"user_id": user_id}, {"$setOnInsert": data}, upsert=True)

    async def get_user(self, user_id):
        return await self.db.users.find_one({"user_id": user_id})

    async def update_user(self, user_id, data):
        await self.db.users.update_one({"user_id": user_id}, {"$set": data})

    async def inc_user(self, user_id, field, amt=1):
        await self.db.users.update_one({"user_id": user_id}, {"$inc": {field: amt}})

    async def add_berries(self, user_id, amt):
        await self.inc_user(user_id, "berries", amt)
        await self.inc_user(user_id, "total_earned", amt)

    async def add_berries_raw(self, user_id, amt):
        await self.inc_user(user_id, "berries", amt)

    async def remove_berries(self, user_id, amt):
        u = await self.get_user(user_id)
        if u and u.get("berries", 0) >= amt:
            await self.inc_user(user_id, "berries", -amt)
            return True
        return False

    async def get_berries(self, user_id):
        u = await self.get_user(user_id)
        return u.get("berries", 0) if u else 0

    async def get_inventory(self, user_id):
        u = await self.get_user(user_id)
        return u.get("inventory", {}) if u else {}

    async def add_to_inventory(self, user_id, item, qty=1):
        inv = await self.get_inventory(user_id)
        inv[item] = inv.get(item, 0) + qty
        await self.update_user(user_id, {"inventory": inv})

    async def remove_from_inventory(self, user_id, item, qty=1):
        inv = await self.get_inventory(user_id)
        if inv.get(item, 0) >= qty:
            inv[item] -= qty
            if inv[item] <= 0: del inv[item]
            await self.update_user(user_id, {"inventory": inv})
            return True
        return False

    async def is_premium(self, user_id):
        u = await self.get_user(user_id)
        if u and u.get("is_premium"):
            if u.get("premium_expiry") and datetime.now() > u["premium_expiry"]:
                await self.update_user(user_id, {"is_premium": False, "premium_expiry": None})
                return False
            return True
        return False

    async def set_premium(self, user_id, days):
        expiry = datetime.now() + timedelta(days=days)
        await self.update_user(user_id, {"is_premium": True, "premium_expiry": expiry})

    async def remove_premium(self, user_id):
        await self.update_user(user_id, {"is_premium": False, "premium_expiry": None})

    async def get_top_users(self, field, limit=10):
        cursor = self.db.users.find({"banned": False}).sort(field, -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def user_count(self):
        return await self.db.users.count_documents({"banned": False})

    # ---- Bank ----
    async def bank_balance(self, user_id):
        u = await self.get_user(user_id)
        return u.get("bank", 0) if u else 0

    async def bank_deposit(self, user_id, amt):
        bal = await self.get_berries(user_id)
        if bal < amt: return False
        await self.inc_user(user_id, "berries", -amt)
        await self.inc_user(user_id, "bank", amt)
        return True

    async def bank_withdraw(self, user_id, amt):
        bal = await self.bank_balance(user_id)
        if bal < amt: return False
        await self.inc_user(user_id, "bank", -amt)
        await self.inc_user(user_id, "berries", amt)
        return True

    async def apply_bank_interest(self, user_id):
        u = await self.get_user(user_id)
        if not u: return 0
        last = u.get("last_interest")
        now = datetime.now()
        if last and (now - last).days < 1: return 0
        bank = u.get("bank", 0)
        if bank <= 0: return 0
        interest = max(1, int(bank * 0.05))
        await self.inc_user(user_id, "bank", interest)
        await self.update_user(user_id, {"last_interest": now})
        return interest

    # ---- XP / Levels ----
    async def add_xp(self, user_id, amt=5):
        u = await self.get_user(user_id)
        if not u: return None
        await self.inc_user(user_id, "xp", amt)
        await self.inc_user(user_id, "total_messages")
        xp = u.get("xp", 0) + amt
        level = u.get("level", 1)
        needed = level * 100
        if xp >= needed:
            await self.inc_user(user_id, "level")
            await self.update_user(user_id, {"xp": xp - needed})
            return level + 1
        return None

    def calc_level(self, xp):
        level = 1
        needed = 100
        while xp >= needed:
            xp -= needed
            level += 1
            needed = level * 100
        return level, xp, needed

    # ---- Characters / Gacha ----
    async def get_characters(self, user_id):
        u = await self.get_user(user_id)
        return u.get("characters", {}) if u else {}

    async def add_character(self, user_id, char_name, rarity):
        chars = await self.get_characters(user_id)
        if char_name in chars:
            chars[char_name]["count"] += 1
        else:
            chars[char_name] = {"rarity": rarity, "count": 1, "favorite": False}
        await self.update_user(user_id, {"characters": chars})
        return char_name

    # ---- Achievements ----
    async def unlock_achievement(self, user_id, ach):
        u = await self.get_user(user_id)
        if not u: return False
        achs = u.get("achievements", [])
        if ach in achs: return False
        achs.append(ach)
        await self.update_user(user_id, {"achievements": achs})
        return True

    # ---- Lotterry ----
    async def get_lottery_pool(self):
        doc = await self.db.lottery.find_one({"_id": "pool"})
        return doc.get("pool", 0) if doc else 0

    async def add_lottery_pool(self, amt):
        await self.db.lottery.update_one({"_id": "pool"}, {"$inc": {"pool": amt}}, upsert=True)

    async def reset_lottery_pool(self):
        await self.db.lottery.update_one({"_id": "pool"}, {"$set": {"pool": 0}}, upsert=True)

    async def lottery_buy_ticket(self, user_id, tickets=1):
        cost = tickets * 50
        bal = await self.get_berries(user_id)
        if bal < cost: return False
        await self.remove_berries(user_id, cost)
        await self.inc_user(user_id, "lottery_tickets", tickets)
        await self.add_lottery_pool(cost)
        return True

    # ---- Blacklist / Whitelist ----
    async def blacklist_chat(self, chat_id):
        await self.db.blacklist.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)

    async def whitelist_chat(self, chat_id):
        await self.db.blacklist.delete_one({"chat_id": chat_id})

    async def is_blacklisted(self, chat_id):
        return bool(await self.db.blacklist.find_one({"chat_id": chat_id}))

    async def get_blacklist(self):
        cursor = self.db.blacklist.find({})
        return await cursor.to_list(length=None)

    # ---- Owners / Co-owners ----
    async def add_co_owner(self, user_id):
        await self.db.co_owners.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

    async def remove_co_owner(self, user_id):
        await self.db.co_owners.delete_one({"user_id": user_id})

    async def is_co_owner(self, user_id):
        return bool(await self.db.co_owners.find_one({"user_id": user_id}))

    async def is_owner_or_co(self, user_id):
        if user_id == Config.OWNER_ID:
            return True
        return await self.is_co_owner(user_id)

    async def get_co_owners(self):
        cursor = self.db.co_owners.find({})
        return await cursor.to_list(length=None)

    # ---- Auth Users ----
    async def add_auth_user(self, user_id, perms=None):
        if perms is None:
            perms = {"play": True, "skip": True, "pause": True, "resume": True,
                     "stop": True, "queue": True, "volume": True, "game": True,
                     "playlist": True, "radio": True, "vplay": True}
        await self.db.auth_users.update_one({"user_id": user_id},
            {"$set": {"user_id": user_id, "permissions": perms}}, upsert=True)

    async def remove_auth_user(self, user_id):
        await self.db.auth_users.delete_one({"user_id": user_id})

    async def get_auth_user(self, user_id):
        return await self.db.auth_users.find_one({"user_id": user_id})

    async def update_auth_perms(self, user_id, perms):
        await self.db.auth_users.update_one({"user_id": user_id}, {"$set": {"permissions": perms}})

    async def get_all_auth_users(self):
        cursor = self.db.auth_users.find({})
        return await cursor.to_list(length=None)

    async def check_auth(self, user_id, command):
        if user_id == Config.OWNER_ID:
            return True
        if await self.is_co_owner(user_id):
            return True
        au = await self.get_auth_user(user_id)
        if au and au.get("permissions", {}).get(command, False):
            return True
        return False

    # ---- Groups / Chats ----
    async def get_chat_settings(self, chat_id):
        defaults = {"volume": Config.DEFAULT_VOLUME, "loop": False, "autoplay": False,
                    "autoleave": True, "autoleave_time": 300, "language": "en",
                    "nightmode": False, "equalizer": "default", "welcome": True,
                    "welcome_msg": "", "goodbye_msg": "",
                    "reaction": True, "limit": Config.MAX_QUEUE,
                    "warns": {}, "tagall": True,
                    "anti_spam": False, "caps_limit": 70, "bad_words": [],
                    "spawn_monsters": True, "spawn_interval": 80}
        s = await self.db.chat_settings.find_one({"chat_id": chat_id})
        if s:
            defaults.update(s)
        return defaults

    async def set_chat_settings(self, chat_id, settings):
        await self.db.chat_settings.update_one({"chat_id": chat_id}, {"$set": settings}, upsert=True)

    async def get_chat_count(self):
        return await self.db.chat_settings.count_documents({})

    # ---- Warnings ----
    async def warn_user(self, chat_id, user_id, reason, admin_id):
        warns = (await self.get_chat_settings(chat_id)).get("warns", {})
        uid = str(user_id)
        if uid not in warns:
            warns[uid] = []
        warns[uid].append({"reason": reason, "admin": admin_id, "time": datetime.now()})
        await self.set_chat_settings(chat_id, {"warns": warns})
        return len(warns[uid])

    async def remove_warns(self, chat_id, user_id):
        warns = (await self.get_chat_settings(chat_id)).get("warns", {})
        warns.pop(str(user_id), None)
        await self.set_chat_settings(chat_id, {"warns": warns})

    async def get_warns(self, chat_id, user_id):
        warns = (await self.get_chat_settings(chat_id)).get("warns", {})
        return warns.get(str(user_id), [])

    # ---- Playlists ----
    async def get_playlist(self, user_id):
        u = await self.get_user(user_id)
        if u:
            return u.get("playlists", {})
        return {}

    async def save_playlist(self, user_id, playlists):
        await self.update_user(user_id, {"playlists": playlists})

    async def get_playlist_limit(self, user_id):
        if await self.is_premium(user_id):
            return Config.PREMIUM_PLAYLIST_LIMIT
        return Config.DEFAULT_PLAYLIST_LIMIT

    async def get_queue_size(self, user_id):
        if await self.is_premium(user_id):
            return Config.PREMIUM_MAX_QUEUE
        return Config.MAX_QUEUE

    # ---- Bot Config (PM Settings) ----
    async def get_bot_config(self):
        c = await self.db.bot_config.find_one({"_id": "main"})
        if not c:
            c = {"support_url": "https://t.me/your_support", "updates_url": "https://t.me/your_channel",
                 "start_img": "", "play_img": "", "queue_img": "", "maintenance": False,
                 "reaction_emoji": Config.REACTION_EMOJI, "greeting": True,
                 "earn_links": {"earn1": "https://t.me/zenii_X_music_bot?start=earn1",
                                "earn2": "https://t.me/zenii_X_music_bot?start=earn2",
                                "earn3": "https://t.me/zenii_X_music_bot?start=earn3",
                                "earn4": "https://t.me/zenii_X_music_bot?start=earn4",
                                "earn5": "https://t.me/zenii_X_music_bot?start=earn5"},
                 "berry_rates": {"earn1": 50, "earn2": 75, "earn3": 100, "earn4": 150, "earn5": 200},
                 "shop_items": {
                     "🍫 Chocolate": {"price": 100, "description": "Sweet chocolate treat (use: +10🫐)"},
                     "🍺 Beer": {"price": 150, "description": "Cold refreshing beer (use: +5XP)"},
                     "💕 Girlfriend": {"price": 5000, "description": "Virtual anime gf (use: +50🫐 daily)"},
                     "🎟️ Lottery Ticket": {"price": 50, "description": "Enter the lottery (draws daily)"},
                     "⚔️ Sword": {"price": 2000, "description": "+5 damage in monster battles"},
                     "🛡️ Shield": {"price": 2500, "description": "+10 HP in monster battles"},
                     "💊 HP Potion": {"price": 500, "description": "Heal 25 HP in battle"},
                     "🎴 Mystery Box": {"price": 1000, "description": "Random item or berries!"},
                     "⭐ Premium 1D": {"price": 1500, "description": "1 Day Premium (worth 3 days earning)"},
                     "⭐ Premium 7D": {"price": 9000, "description": "7 Days Premium"},
                 }}
            await self.db.bot_config.insert_one({"_id": "main", **c})
        return c

    async def update_bot_config(self, data):
        await self.db.bot_config.update_one({"_id": "main"}, {"$set": data}, upsert=True)

    # ---- Active Calls ----
    async def add_active_call(self, chat_id):
        await self.db.active_calls.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)

    async def remove_active_call(self, chat_id):
        await self.db.active_calls.delete_one({"chat_id": chat_id})

    async def get_active_calls(self):
        cursor = self.db.active_calls.find({})
        return await cursor.to_list(length=None)

    async def active_calls_count(self):
        return await self.db.active_calls.count_documents({})

    # ---- Logs ----
    async def add_log(self, log_type, data):
        log = {"type": log_type, "data": data, "time": datetime.now()}
        await self.db.logs.insert_one(log)

    async def get_logs(self, limit=50):
        cursor = self.db.logs.find().sort("time", -1).limit(limit)
        return await cursor.to_list(length=limit)

    # ---- Stats ----
    async def get_bot_stats(self):
        users = await self.user_count()
        groups = await self.get_chat_count()
        calls = await self.active_calls_count()
        return {"users": users, "groups": groups, "active_calls": calls}
