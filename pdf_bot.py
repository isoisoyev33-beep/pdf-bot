import os
import asyncio
import logging
import img2pdf
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile

# --- SOZLAMALAR ---
# Tokenni o'zgartirmang, u rasmda ko'rsatilgani bilan bir xil
PDF_BOT_TOKEN = '8359916106:AAGNUVEHKKHTKLf_jKi5E9Uqbb5Bu79xBD4'
bot = Bot(token=PDF_BOT_TOKEN)
dp = Dispatcher()

# Rasmlarni vaqtinchalik saqlash uchun lug'at
user_images = {}

# Render jurnallarida ko'rinishi uchun loglarni sozlash
logging.basicConfig(level=logging.INFO)


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Salom! Menga bir nechta rasm yuboring, men ularni PDF qilib beraman. Rasmlarni yuborib bo'lgach /done buyrug'ini bosing.")


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_images:
        user_images[user_id] = []

    # Eng sifatli rasmni tanlash
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)

    # Downloads papkasini tekshirish va yaratish
    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{photo.file_id}.jpg"

    # Rasmni yuklab olish
    await bot.download_file(file_info.file_path, file_path)
    user_images[user_id].append(file_path)
    await message.answer(f"{len(user_images[user_id])}-chi rasm qabul qilindi.")


@dp.message(Command("done"))
async def convert_to_pdf(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_images or not user_images[user_id]:
        await message.answer("Hali rasm yubormadingiz. Iltimos, avval rasm yuboring.")
        return

    pdf_name = f"result_{user_id}.pdf"
    pdf_path = os.path.join("downloads", pdf_name)

    try:
        # Rasmlarni PDF ga aylantirish
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(user_images[user_id]))

        # Tayyor PDF faylni yuborish
        document = FSInputFile(pdf_path)
        await message.answer_document(document, caption="Mana sizning PDF faylingiz! ✅")

        # Ishlatilgan rasmlarni o'chirish
        for img in user_images[user_id]:
            if os.path.exists(img):
                os.remove(img)
        user_images[user_id] = []

        # PDF faylni o'chirish (serverda joy egallamasligi uchun)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    except Exception as e:
        logging.error(f"Xato yuz berdi: {e}")
        await message.answer(f"Xatolik yuz berdi: {e}")


# Render uchun asosiy ishga tushirish funksiyasi
async def main():
    logging.info("PDF bot ishga tushdi va so'rovlarni kutmoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.")
