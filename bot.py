import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web
import yt_dlp

# --- SOZLAMALAR ---
API_TOKEN = '7290038309:AAEPc1DgeYTbD9ZDFfsdC7IiZUCIYN99rdE'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Render uchun port ochish (O'chib qolmasligi uchun)
async def handle(request):
    return web.Response(text="Bot ishlayapti!")


async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


# --- YUKLOVCHI FUNKSIYA ---
def download_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


# --- HANDLERLAR ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply("Salom! 3-versiyadagi botingiz ishga tushdi. YouTube yoki Instagram linkini yuboring.")


@dp.message()
async def handle_message(message: types.Message):
    url = message.text
    if url and ("youtube.com" in url or "youtu.be" in url or "instagram.com" in url):
        msg = await message.answer("Video tayyorlanmoqda, iltimos kuting...")
        try:
            file_path = await asyncio.to_thread(download_video, url)
            video_file = types.FSInputFile(file_path)
            await message.answer_video(video_file, caption="Mana sizning videongiz!")
            os.remove(file_path)
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"Xatolik: {e}")
    elif url:
        await message.answer("Iltimos, faqat YouTube yoki Instagram linkini yuboring.")


# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Portni va botni birga ishga tushiramiz
    await asyncio.gather(
        start_webserver(),
        dp.start_polling(bot)
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())