import os
import asyncio
import logging
import img2pdf
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile

# --- SOZLAMALAR ---
# Tokenni o'zingizniki bilan almashtiring (image_bec8c4.jpg dagi kabi)
PDF_BOT_TOKEN = '8359916106:AAGNUVEHKKHTKLf_jKi5E9Uqbb5Bu79xBD4'
bot = Bot(token=PDF_BOT_TOKEN)
dp = Dispatcher()

# Rasmlarni vaqtinchalik saqlash uchun ro'yxat
user_images = {}

# Loglarni sozlash (Render'da ko'rinishi uchun)
logging.basicConfig(level=logging.INFO)


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Salom! Menga rasmlar yuboring, men ularni bitta PDF qilib beraman. Rasmlarni yuborib bo'lgach /done buyrug'ini bosing.")


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_images:
        user_images[user_id] = []

    # Rasmni yuklab olish
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = f"downloads/{photo.file_id}.jpg"

    # downloads papkasi bo'lmasa yaratish
    os.makedirs("downloads", exist_ok=True)

    await bot.download_file(file_info.file_path, file_path)
    user_images[user_id].append(file_path)
    await message.answer(f"{len(user_images[user_id])}-chi rasm qabul qilindi.")


@dp.message(Command("done"))
async def convert_to_pdf(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_images or not user_images[user_id]:
        await message.answer("Hali rasm yubormadingiz.")
        return

    pdf_path = f"downloads/result_{user_id}.pdf"

    try:
        # Rasmlarni PDF ga o'tkazish
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(user_images[user_id]))

        # PDF ni yuborish
        document = FSInputFile(pdf_path)
        await message.answer_document(document, caption="Sizning PDF faylingiz tayyor!")

        # Tozalash
        for img in user_images[user_id]:
            if os.path.exists(img):
                os.remove(img)
        user_images[user_id] = []
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    except Exception as e:
        await message.answer(f"Xato yuz berdi: {e}")


# Render uchun asosiy ishga tushirish funksiyasi
async def main():
    logging.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")