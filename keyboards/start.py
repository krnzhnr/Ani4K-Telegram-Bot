from aiogram.types import ReplyKeyboardMarkup
from keyboards.create_post_kb import create_post_start_kb, CreatePostCallbackActions
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def start_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text='Создать пост')
    )
    return builder.as_markup(resize_keyboard=True)
