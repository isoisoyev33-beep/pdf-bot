import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from PIL import Image
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# SIZNING TOKENINGIZ
API_TOKEN = '8359916106:AAGNUVEHKKHTKLf_jKi5E9Uqbb5Bu79xBD4'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class PDFState(StatesGroup):
    collecting_photos = State()
    waiting_for_name = State()


kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton("✅ Rasmlar tugadi (PDF qilish)"))


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Salom! PDF qilmoqchi bo'lgan barcha rasmlaringizni yuboring. Tugatganingizdan so'ng pastdagi tugmani bosing.",
        reply_markup=kb)
    await PDFState.collecting_photos.set()


@dp.message_handler(content_types=['photo'], state=PDFState.collecting_photos)
async def handle_photos(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(photo_id)
    await state.update_data(photos=photos)
    await message.answer(f"{len(photos)}-chi rasm qabul qilindi.")


@dp.message_handler(lambda message: message.text == "✅ Rasmlar tugadi (PDF qilish)", state=PDFState.collecting_photos)
async def finish_collection(message: types.Message, state: FSMContext):
    await message.answer("PDF fayl uchun nom yozing:", reply_markup=types.ReplyKeyboardRemove())
    await PDFState.waiting_for_name.set()


@dp.message_handler(state=PDFState.waiting_for_name)
async def create_pdf(message: types.Message, state: FSMContext):
    file_name = f"{message.text}.pdf"
    data = await state.get_data()
    photo_ids = data.get('photos', [])

    await message.answer("PDF tayyorlanmoqda, kuting...")
    image_list = []

    for i, p_id in enumerate(photo_ids):
        path = f"img_{i}.jpg"
        file = await bot.get_file(p_id)
        await bot.download_file(file.file_path, path)
        image_list.append(Image.open(path).convert('RGB'))
        os.remove(path)

    if image_list:
        image_list[0].save(file_name, save_all=True, append_images=image_list[1:])
        with open(file_name, 'rb') as doc:
            await message.answer_document(doc, caption=f"Tayyor! {len(image_list)} ta rasm bitta faylda.")
        os.remove(file_name)

    await state.finish()
    await PDFState.collecting_photos.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)