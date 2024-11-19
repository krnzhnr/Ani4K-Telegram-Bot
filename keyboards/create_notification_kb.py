from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram import types
from keyboards.create_post_kb import CreatePostCallbackActions


class CreateNotificationCallbackActions(CallbackData, prefix='createnotification'):
    action: str


# ============ КЛАВИАТУРА ВЫБОРА КАНАЛА ============

def create_noti_channel_selection_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Основной', callback_data=CreateNotificationCallbackActions(action='noti_main_channel')
    )
    builder.button(
        text='Тестовый', callback_data=CreateNotificationCallbackActions(action='noti_test_channel')
    )
    return builder.as_markup()


# ============ КЛАВИАТУРА ВЫБОРА ТИПА РЕЛИЗА ============

def create_noti_release_type_selection():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Фильм', callback_data=CreateNotificationCallbackActions(action='film_selected')
    )
    builder.button(
        text='Сериал', callback_data=CreateNotificationCallbackActions(action='series_selected')
    )
    return builder.as_markup()


# ============ КЛАВИАТУРА "СКОЛЬКО СТАЛО ДОСТУПНО ЭПИЗОДОВ" ============

def create_noti_howmuchepisedes_selection_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Один', callback_data=CreateNotificationCallbackActions(action='one_episode_selected')
    )
    builder.button(
        text='Несколько', callback_data=CreateNotificationCallbackActions(action='many_episodes_selected')
    )
    builder.button(
        text='Отменить', callback_data=CreatePostCallbackActions(action='creation_cancel')
    )
    builder.adjust(2)
    return builder.as_markup()


# ============ КНОПКА "ТЕСТОВЫЙ", КОГДА ПОЛЬЗОВАТЕЛЬ ПЫТАЛСЯ ЗАПОСТИТЬ В ОСНОВНОЙ КАНАЛ ============

def create_noti_channel_test():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Тестовый', callback_data=CreateNotificationCallbackActions(action='noti_test_channel')
    )
    return builder.as_markup()


# ============ КЛАВИАТУРА ДЛЯ ПУБЛИКАЦИИ ИЛИ ОТМЕНЫ НА ЭТАПЕ ПРЕДПРОСМОТРА ГОТОВОГО УВЕДОМЛЕНИЯ ============

def create_noti_finish_kb():
    from handlers.create_notification import notification
    builder = InlineKeyboardBuilder()
    # builder.row(types.InlineKeyboardButton(
    #     text='Перейти в Ani4K HUB', url='https://t.me/ani4k_ru_hub'
    # ))
    # builder.row(types.InlineKeyboardButton(
    #     text='Смотреть', url=notification['link']
    # ))
    builder.button(
        text='Опубликовать', callback_data=CreateNotificationCallbackActions(action='noti_publish')
    )
    builder.button(
        text='Отменить', callback_data=CreateNotificationCallbackActions(action='noti_finish_cancel')
    )
    builder.adjust(1)
    return builder.as_markup()
