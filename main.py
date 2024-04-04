from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import time
API_TOKEN = '7173280899:AAFSxyOgPdXVYCVvV2Ad26sz0ftk-Uo-MA4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
isSend = False
users_media = {}


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    global users_media,isSend
    isSend = False
    users_media = {}
    inline_btn = InlineKeyboardButton('first btn', callback_data='button1')
    inline_kb = InlineKeyboardMarkup().add(inline_btn)
    await message.reply("Здравствуйте! Добро пожаловать", reply_markup=inline_kb)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'button1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Напишите название ЖК')
    users_media[callback_query.from_user.id] = {'media': [], 'name': None, 'surname': None}


@dp.message_handler()
async def process_text(message: types.Message):
    user_id = message.from_user.id
    if user_id in users_media:
        if users_media[user_id]['name'] is None:
            users_media[user_id]['name'] = message.text
            await message.answer("Напишите описание")
        elif users_media[user_id]['surname'] is None:
            users_media[user_id]['surname'] = message.text
            await message.answer("Отправьте фотки или видео ЖК")


@dp.message_handler(content_types=['photo', 'video'])
async def process_media(message: types.Message):
    print(message.media_group_id)
    global isSend
    user_id = message.from_user.id
    if user_id in users_media:
        users_media[user_id]['media'].append(
            {'type': message.content_type, 'media': message[message.content_type][-1].file_id})
        if isSend:
           await send_media_with_info(user_id, users_media[user_id]['media'], users_media[user_id]['name'],
                                   users_media[user_id]['surname'])
        time.sleep(3)
        isSend = True
        await message.answer("Принято!")


@dp.message_handler(content_types=['document'])
async def process_document(message: types.Message):
    await message.answer("К сожалению, поддерживаются только фотографии и видео.")


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def process_other_content(message: types.Message):
    await message.answer("К сожалению, поддерживаются только фотографии и видео.")


async def send_media_with_info(user_id, media, name, surname):
    media_group = []
    for item in media:
        if item['type'] == 'photo':
            media_group.append(types.InputMediaPhoto(media=item['media']))
        elif item['type'] == 'video':
            media_group.append(types.InputMediaVideo(media=item['media'], caption=f"Имя: {name}\nФамилия: {surname}"))
        media_group[0].caption = f"Имя: {name}\nФамилия: {surname}"
    await bot.send_media_group(user_id, media=media_group)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)