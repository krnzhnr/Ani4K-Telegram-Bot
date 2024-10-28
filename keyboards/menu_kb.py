from aiogram.types import ReplyKeyboardMarkup
from keyboards.create_post_kb import create_post_start_kb, CreatePostCallbackActions
from keyboards.create_notification_kb import CreateNotificationCallbackActions
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types


def start_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text='Меню')
    )
    return builder.as_markup(resize_keyboard=True)

def menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Создать', callback_data=CreatePostCallbackActions(action='create')
    )
    return builder.as_markup()

def create_type_select_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Анонс', callback_data=CreatePostCallbackActions(action='create_announcement')
    )
    builder.button(
        text='Уведомление', callback_data=CreateNotificationCallbackActions(action='create_notification')
    )
    return builder.as_markup()

def creation_cancel_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отменить', callback_data=CreatePostCallbackActions(action='creation_cancel')
    )
    return builder.as_markup()