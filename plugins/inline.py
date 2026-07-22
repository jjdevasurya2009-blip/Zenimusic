from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Client.on_inline_query()
async def inline_search(client: Client, query: InlineQuery):
    text = query.query.strip()
    results = []
    if text:
        try:
            from yt_dlp import YoutubeDL
            with YoutubeDL({"quiet":True,"no_warnings":True,"extract_flat":True}) as ydl:
                search = ydl.extract_info(f"ytsearch5:{text}", download=False)
                if 'entries' in search:
                    for entry in search['entries']:
                        d = entry.get('duration',0)
                        title = entry.get('title','Unknown')[:64]
                        uploader = entry.get('uploader','?')
                        url = entry.get('webpage_url','')
                        thumb = entry.get('thumbnail','')
                        results.append(InlineQueryResultArticle(
                            title=title,
                            description=f"{uploader} | {d//60}:{d%60:02d}",
                            thumb_url=thumb,
                            input_message_content=InputTextMessageContent(
                                f"🎵 <b>{title}</b>\n👤 {uploader}\n⏱ {d//60}:{d%60:02d}"
                            ),
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("▶️ Play", callback_data=f"play_{url}"),
                                 InlineKeyboardButton("📥 Download", callback_data=f"dl_inline_{url}")],
                                [InlineKeyboardButton("🔗 Share", url=url)]
                            ])
                        ))
        except: pass
    if not results:
        results.append(InlineQueryResultArticle(
            title="Search music!",
            description="Type a song name to search",
            input_message_content=InputTextMessageContent(
                "🔍 Search songs by typing name!\n\nExample: @zenii_X_music_bot Believer"
            )
        ))
    await query.answer(results=results[:10], cache_time=1, is_personal=True)
