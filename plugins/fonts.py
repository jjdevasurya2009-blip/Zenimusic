from pyrogram import Client, filters
from pyrogram.types import Message

FONTS = {
    "smallcaps": {
        "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ",
        "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
        "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "s", "t": "ᴛ", "u": "ᴜ",
        "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
    },
    "fancy": {
        "a": "𝒶", "b": "𝒷", "c": "𝒸", "d": "𝒹", "e": "𝑒", "f": "𝒻", "g": "𝑔",
        "h": "𝒽", "i": "𝒾", "j": "𝒿", "k": "𝓀", "l": "𝓁", "m": "𝓂", "n": "𝓃",
        "o": "𝑜", "p": "𝓅", "q": "𝓆", "r": "𝓇", "s": "𝓈", "t": "𝓉", "u": "𝓊",
        "v": "𝓋", "w": "𝓌", "x": "𝓍", "y": "𝓎", "z": "𝓏",
    },
    "fraktur": {
        "a": "𝔞", "b": "𝔟", "c": "𝔠", "d": "𝔡", "e": "𝔢", "f": "𝔣", "g": "𝔤",
        "h": "𝔥", "i": "𝔦", "j": "𝔧", "k": "𝔨", "l": "𝔩", "m": "𝔪", "n": "𝔫",
        "o": "𝔬", "p": "𝔭", "q": "𝔮", "r": "𝔯", "s": "𝔰", "t": "𝔱", "u": "𝔲",
        "v": "𝔳", "w": "𝔴", "x": "𝔵", "y": "𝔶", "z": "𝔷",
    },
    "bold": {
        "a": "𝗮", "b": "𝗯", "c": "𝗰", "d": "𝗱", "e": "𝗲", "f": "𝗳", "g": "𝗴",
        "h": "𝗵", "i": "𝗶", "j": "𝗷", "k": "𝗸", "l": "𝗹", "m": "𝗺", "n": "𝗻",
        "o": "𝗼", "p": "𝗽", "q": "𝗾", "r": "𝗿", "s": "𝘀", "t": "𝘁", "u": "𝘂",
        "v": "𝘃", "w": "𝘄", "x": "𝘅", "y": "𝘆", "z": "𝘇",
    },
    "monospace": {
        "a": "𝚊", "b": "𝚋", "c": "𝚌", "d": "𝚍", "e": "𝚎", "f": "𝚏", "g": "𝚐",
        "h": "𝚑", "i": "𝚒", "j": "𝚓", "k": "𝚔", "l": "𝚕", "m": "𝚖", "n": "𝚗",
        "o": "𝚘", "p": "𝚙", "q": "𝚚", "r": "𝚛", "s": "𝚜", "t": "𝚝", "u": "𝚞",
        "v": "𝚟", "w": "𝚠", "x": "𝚡", "y": "𝚢", "z": "𝚣",
    },
    "doublestruck": {
        "a": "𝕒", "b": "𝕓", "c": "𝕔", "d": "𝕕", "e": "𝕖", "f": "𝕗", "g": "𝕘",
        "h": "𝕙", "i": "𝕚", "j": "𝕛", "k": "𝕜", "l": "𝕝", "m": "𝕞", "n": "𝕟",
        "o": "𝕠", "p": "𝕡", "q": "𝕢", "r": "𝕣", "s": "𝕤", "t": "𝕥", "u": "𝕦",
        "v": "𝕧", "w": "𝕨", "x": "𝕩", "y": "𝕪", "z": "𝕫",
    },
}

FONT_NAMES = list(FONTS.keys())

def convert_font(text: str, font_name: str) -> str:
    mapping = FONTS.get(font_name, {})
    result = []
    for ch in text:
        lower = ch.lower()
        if lower in mapping:
            is_upper = ch.isupper()
            converted = mapping[lower]
            result.append(converted.upper() if is_upper and font_name != "smallcaps" else converted)
        else:
            result.append(ch)
    return "".join(result)

@Client.on_message(filters.command(["smallcaps","sm"]))
async def smallcaps_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        text = "Example text in small caps"
    else:
        text = message.text.split(None, 1)[1]
    converted = convert_font(text, "smallcaps")
    await message.reply(f"<b>Small Caps:</b>\n<code>{converted}</code>")

@Client.on_message(filters.command(["fancy","script"]))
async def fancy_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        text = "Example text in fancy script"
    else:
        text = message.text.split(None, 1)[1]
    converted = convert_font(text, "fancy")
    await message.reply(f"<b>Fancy Script:</b>\n<code>{converted}</code>")

@Client.on_message(filters.command(["fraktur","gothic"]))
async def fraktur_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        text = "Example text in fraktur"
    else:
        text = message.text.split(None, 1)[1]
    converted = convert_font(text, "fraktur")
    await message.reply(f"<b>Fraktur Gothic:</b>\n<code>{converted}</code>")

@Client.on_message(filters.command(["boldfont","bb"]))
async def boldfont_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        text = "Example text in bold"
    else:
        text = message.text.split(None, 1)[1]
    converted = convert_font(text, "bold")
    await message.reply(f"<b>Bold Sans:</b>\n<code>{converted}</code>")

@Client.on_message(filters.command(["monofont","mono"]))
async def monofont_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        text = "Example text in monospace"
    else:
        text = message.text.split(None, 1)[1]
    converted = convert_font(text, "monospace")
    await message.reply(f"<b>Monospace:</b>\n<code>{converted}</code>")

@Client.on_message(filters.command(["doublestruck","ds"]))
async def ds_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        text = "Example text in double struck"
    else:
        text = message.text.split(None, 1)[1]
    converted = convert_font(text, "doublestruck")
    await message.reply(f"<b>Double Struck:</b>\n<code>{converted}</code>")

@Client.on_message(filters.command(["fontlist","fonts","styles"]))
async def font_list_cmd(client: Client, message: Message):
    sample = "Hello World"
    text = "<b>🎨 Available Font Styles</b>\n\n"
    for name in FONT_NAMES:
        converted = convert_font(sample, name)
        text += f"<b>/{name}</b> — {converted}\n"
    text += "\nUsage: /<style> <text>\nExample: /smallcaps hello"
    await message.reply(text)
