from functools import wraps
from pyrogram.enums import ChatType
from config import Config

def group_only(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            return await func(client, message, *args, **kwargs)
        await message.reply("❌ Group only command.")
        return None
    return wrapper

def owner_only(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        if message.from_user and message.from_user.id == Config.OWNER_ID:
            return await func(client, message, *args, **kwargs)
        await message.reply("❌ Owner only.")
        return None
    return wrapper

def check_auth(cmd_name):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message, *args, **kwargs):
            uid = message.from_user.id
            if uid == Config.OWNER_ID:
                return await func(client, message, *args, **kwargs)
            db = client.bot_instance.db
            if await db.is_co_owner(uid):
                return await func(client, message, *args, **kwargs)
            au = await db.get_auth_user(uid)
            if au and au.get("permissions", {}).get(cmd_name, False):
                return await func(client, message, *args, **kwargs)
            await message.reply(f"❌ No permission for /{cmd_name}")
            return None
        return wrapper
    return decorator
