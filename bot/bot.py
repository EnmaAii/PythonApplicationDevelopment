import asyncio
import traceback
import os
from aiogram import Bot, Dispatcher, types
from aiogram import exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from recognition import recognition
from translator import translate_text

BOT_TOKEN = "Здесь должен быть токен для доступа к HTTP API"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создаем директорию для изображений, если она не существует
if not os.path.exists("images"):
    os.makedirs("images")

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    try:
        await message.answer('Скорее выбирайте, что хотите сделать со своим текстом:', reply_markup=initial_keyboard())
    except exceptions.BotBlocked:
        print(f"Пользователь {message.from_user.id} заблокировал бота.")
    except exceptions.ChatNotFound:
        print(f"Чат {message.chat.id} не найден.")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")
        print(traceback.format_exc())

# Задаем клавиатуру
def initial_keyboard():
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(types.InlineKeyboardButton(text='Распознать 🇬🇧 или 🇷🇺 текст', callback_data='ocr'))
    keyboard_markup.add(types.InlineKeyboardButton(text='Перевести текст с 🇬🇧 на 🇷🇺', callback_data='translate_eng'))
    keyboard_markup.add(types.InlineKeyboardButton(text='Перевести текст с 🇷🇺 на 🇬🇧', callback_data='translate_rus'))
    return keyboard_markup



# Определяем состояния
class Form(StatesGroup):
    waiting_for_photo = State()
    waiting_for_photo_translate_eng = State()
    waiting_for_photo_translate_rus = State()

@dp.callback_query_handler(lambda call: call.data in ['ocr', 'translate_eng', 'translate_rus'])
async def process_callback_query(call: types.CallbackQuery, state: FSMContext):
    """Обработчик всех callback_query"""
    if call.data == 'ocr':
      await Form.waiting_for_photo.set()
      await call.message.answer("Загрузите изображение для распознавания текста на английском или русском:")
    elif call.data == 'translate_eng':
      await Form.waiting_for_photo_translate_eng.set()
      await call.message.answer("Загрузите изображение для перевода английского текста на русский:")
    elif call.data == 'translate_rus':
      await Form.waiting_for_photo_translate_rus.set()
      await call.message.answer("Загрузите изображение для перевода русского текста на английский:")

    await call.answer()

# Обработчики текста
@dp.message_handler(content_types = types.ContentType.TEXT)
async def handle_text(message: types.Message):
    await message.answer(
            'Неверный формат. Пожалуйста, снова выберите действие, которое хотите сделать и загружайте изображение!',
            reply_markup=initial_keyboard())
@dp.message_handler(content_types=types.ContentType.TEXT, state=[Form.waiting_for_photo, Form.waiting_for_photo_translate_eng, Form.waiting_for_photo_translate_rus])
async def handle_photo(message: types.Message, state: FSMContext):
    await state.finish()  # Завершаем состояние
    await message.answer(
        'Неверный формат. Пожалуйста, снова выберите действие, которое хотите сделать и загружайте изображение!',
        reply_markup=initial_keyboard())

# Обработчик изображений
@dp.message_handler(content_types=types.ContentType.PHOTO, state=[Form.waiting_for_photo, Form.waiting_for_photo_translate_eng, Form.waiting_for_photo_translate_rus])
async def handle_photo(message: types.Message, state: FSMContext):
    try:
        # Получаем фото с наивысшим разрешением
        photo = message.photo[-1]

        # Скачиваем изображение
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        downloaded_file = await bot.download_file(file_path)

        # Сохраняем изображение на диск
        filename = f"images/{message.from_user.id}_{message.message_id}.jpg" # имя файла уникальное для каждого пользователя и сообщения
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file.read())

        # Вызываем функцию recognition, чтобы получить текст с картинки
        original_text = recognition(filename)

        # В зависимости от состояния, выполняется соответсвующий вывод: считанный текст с картинки; переведенный текст с картинки
        current_state = await state.get_state()
        if current_state == Form.waiting_for_photo.state:
            if original_text:
                await message.reply(original_text)
            else:
                await message.reply("Не удалось распознать текст на изображении.")
        elif current_state == Form.waiting_for_photo_translate_rus.state:
            translated_text = translate_text(original_text, 'ru')
            if translated_text:
                await message.reply(translated_text)
            else:
                await message.reply("Не удалось перевести текст на изображении.")
        else:
            translated_text = translate_text(original_text, 'en')
            if translated_text:
                await message.reply(translated_text)
            else:
                await message.reply("Не удалось перевести текст на изображении.")

        await state.finish()  # Завершаем состояние
        await message.answer(
            'Ваша просьба выполнена, благодарим за использование нашего бота и будем рады помочь вам еще:',
            reply_markup=initial_keyboard())


    except Exception as e:
        print(f"Ошибка при обработке изображения: {e}")
        print(traceback.format_exc())
        await message.answer(
            'Ошибка при обработке изображения. Попробуйте снова:',
            reply_markup=initial_keyboard())
async def on_startup(dispatcher):
    print('Бот запущен')

async def main():
    await on_startup(dp) # Запуск on_startup перед start_polling
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
