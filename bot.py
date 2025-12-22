import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp

# --- SOZLAMALAR ---
API_TOKEN = '7290038309:AAEPc1DgeYTbD9ZDFfsdC7IiZUCIYN99rdE'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


# Yuklash funksiyasi (FFmpeg-siz)
def download_insta(link):
    ydl_opts = {
        # Faqat tayyor videoni yuklashni so'raymiz
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        return ydl.prepare_filename(info)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom! Instagram Reels linkini yuboring, men videoni yuklab beraman. 📥")


@dp.message()
async def handle_link(message: types.Message):
    link = message.text
    if "instagram.com" in link:
        msg = await message.answer("Video yuklanyapti... ⏳")
        try:
            if not os.path.exists('downloads'):
                os.makedirs('downloads')

            video_file = download_insta(link)
            await message.answer_video(types.FSInputFile(video_file), caption="Tayyor! ✅")

            os.remove(video_file)
            await msg.delete()
        except Exception as e:
            await message.answer(f"Xatolik: {e}")
    else:
        await message.answer("Iltimos, Instagram linkini yuboring.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())