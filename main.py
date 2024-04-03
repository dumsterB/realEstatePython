from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage


class MyState(StatesGroup):
    NAME = State()
    SURNAME = State()
    PHOTO = State()


API_TOKEN = '7173280899:AAFSxyOgPdXVYCVvV2Ad26sz0ftk-Uo-MA4'

# Configure bot, dispatcher, and memory storage
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    inline_btn = InlineKeyboardButton('first btn', callback_data='button1')
    inline_kb = InlineKeyboardMarkup().add(inline_btn)
    await message.reply("Здравствуйте! Добро пожаловать", reply_markup=inline_kb)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'button1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Напишите свое имя')
    await MyState.NAME.set()


@dp.message_handler(state=MyState.NAME)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer("Теперь напишите свою фамилию")
    await MyState.SURNAME.set()


@dp.message_handler(state=MyState.SURNAME)
async def process_surname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['surname'] = message.text
    await message.answer("Теперь отправьте ваше фото")
    await MyState.PHOTO.set()


@dp.message_handler(content_types=['photo'], state=MyState.PHOTO)
async def process_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo_id'] = message.photo[-1].file_id
        data['name'] = await state.get_data('name')
        data['surname'] = await state.get_data('surname')
        print(data)

    collected_data = data['name']
    photo_id = data['photo_id']

    caption = f"Имя: {collected_data['name']}\nФамилия: {collected_data['surname']}"

    await bot.send_photo(message.from_user.id, photo_id, caption=caption)
    await state.finish()


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
