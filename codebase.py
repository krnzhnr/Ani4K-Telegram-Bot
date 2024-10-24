import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, html
from aiogram.filters.command import Command, CommandObject, CommandStart
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.types import Message, LinkPreviewOptions
from aiogram.enums import ParseMode
from config_reader import config
from aiogram.client.default import DefaultBotProperties
from datetime import datetime
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from magic_filter import F
import random
from random import randint
import re

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
# Диспетчер
dp = Dispatcher()


class NumbersCallbackFactory(CallbackData, prefix='fabnum'):
    action: str
    value: Optional[int] = None

def get_keyboard_fab():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='-2', callback_data=NumbersCallbackFactory(action='change', value=-2)
    )
    builder.button(
        text='-1', callback_data=NumbersCallbackFactory(action='change', value=-1)
    )
    builder.button(
        text='+1', callback_data=NumbersCallbackFactory(action='change', value=1)
    )
    builder.button(
        text='+2', callback_data=NumbersCallbackFactory(action='change', value=2)
    )
    builder.button(
        text='Подтвердить', callback_data=NumbersCallbackFactory(action='finish')
    )
    builder.adjust(4)
    return builder.as_markup()

async def update_num_text_fab(message: types.Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Укажите число: {new_value}",
            reply_markup=get_keyboard_fab()
        )

@dp.message(Command("numbers_fab"))
async def cmd_numbers_fab(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите число: 0", reply_markup=get_keyboard_fab())

@dp.callback_query(NumbersCallbackFactory.filter(F.action == 'change'))
async def callbacks_num_change_fub(
    callback: types.CallbackQuery,
    callback_data: NumbersCallbackFactory
):
    user_value = user_data.get(callback.from_user.id, 0)
    user_data[callback.from_user.id] = user_value + callback_data.value
    await update_num_text_fab(callback.message, user_value + callback_data.value)
    await callback.answer()

@dp.callback_query(NumbersCallbackFactory.filter(F.action == 'finish'))
async def callbacks_num_finish_fab(callback: types.CallbackQuery):
    user_value = user_data.get(callback.from_user.id, 0)
    await callback.message.edit_text(f'Итого: {user_value}')
    await callback.answer()


#######################################################################



user_data = {}

def get_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text='-1', callback_data='num_decr'),
            types.InlineKeyboardButton(text='+1', callback_data='num_incr')
        ],
        [
            types.InlineKeyboardButton(text='Подтвердить', callback_data='num_finish')
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def update_num_text(message: types.Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f'Укажите число: {new_value}',
            reply_markup=get_keyboard()
        )

@dp.message(Command('numbers'))
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer('Укажите число: 0', reply_markup=get_keyboard())

@dp.callback_query(F.data.startswith('num_'))
async def callbacks_num(callback: types.CallbackQuery):
    user_value = user_data.get(callback.from_user.id, 0)
    action = callback.data.split('_')[1]

    if action == 'incr':
        user_data[callback.from_user.id] = user_value+1
        await update_num_text(callback.message, user_value+1)
    elif action == 'decr':
        user_data[callback.from_user.id] = user_value-1
        await update_num_text(callback.message, user_value-1)
    elif action == 'finish':
        await callback.message.edit_text(f'Итого: {user_value}')
    
    await callback.answer()


#########################################################



@dp.message(Command('random'))
async def random(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='Нажми меня',
        callback_data='random_value'
    ))

    await message.answer(
        'Ща будет прикол',
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == 'random_value')
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(f'{str(randint(1, 10))} мальчиков из боку но пико к тебе придет ночью')
    await callback.answer(
        text='Попався любитель маленьких мальчиков!',
        show_alert=False
    )

#################################################################


@dp.message(Command('buttons'))
async def buttons(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text='Дай кнопки')
    )
    await message.answer(
        'Держи кнопку',
        reply_markup=builder.as_markup()
    )

@dp.message(F.text.lower() == 'дай кнопки')
async def inline_buttons(message: types.Message, bot: Bot):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text='Ani4K Hub', url='https://t.me/ani4k_ru_hub')
    )
    builder.row(types.InlineKeyboardButton(
        text='Ani4K Channel', url='https://t.me/ani4k_ru')
    )

    await message.answer(

        'Держи свои кнопки:',
        reply_markup=builder.as_markup()
    )




#################################################################################

video_ids = []

@dp.message(F.video)
async def echo_video(message: Message):
    try:
        video_ids.append(message.video.file_id)
        await message.reply(f'ID {message.video.file_id} добавлен')
        print(f'Видео с ID {message.video.file_id} добавлено')
    except:
        await message.reply('Что-то не так')

@dp.message(Command('videos'))
async def send_saved_videos(message: Message):
    if len(video_ids) >= 1:
        for video in video_ids:
            await message.answer_video(
                video,
                caption=f'Это видео с ID {video}'
                )
    else:
        await message.answer('Список видео пуст :(')

@dp.message(Command('clear_videos'))
async def clear_videos(message: Message):
    try:
        video_ids.clear()
        await message.answer('Очищено')
    except:
        await message.answer('Что-то пошло не так')

@dp.message(Command('test'))
async def cmd_hello(message: Message):
    await message.answer(
        f'Hello, {html.bold(html.quote(message.from_user.full_name))}'
    )

@dp.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'book_(\d+)'))
))
async def cmd_start_book(
        message: Message,
        command: CommandObject
):
    book_number = command.args.split("_")[1]
    await message.answer(f"Sending book №{book_number}")




# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())