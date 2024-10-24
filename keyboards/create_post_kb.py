from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class ChoiceDubCallbackActions(CallbackData, prefix='dub'):
    dub: str

class CreatePostCallbackActions(CallbackData, prefix='createpost'):
    action: str


def create_post_start_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Создать пост', callback_data=CreatePostCallbackActions(action='start')
    )
    return builder.as_markup()

def create_post_channel_selection():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Основной', callback_data=CreatePostCallbackActions(action='main_channel')
    )
    builder.button(
        text='Тестовый', callback_data=CreatePostCallbackActions(action='test_channel')
    )
    return builder.as_markup()

def choice_dub_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Дублированный', callback_data=ChoiceDubCallbackActions(dub='dubbed')
    )
    builder.button(
        text='Закадровая', callback_data=ChoiceDubCallbackActions(dub='voiceover')
    )
    return builder.as_markup()


def create_post_finish_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Опубликовать', callback_data=CreatePostCallbackActions(action='publish')
    )
    builder.button(
        text='Отменить', callback_data=CreatePostCallbackActions(action='finish_cancel')
    )
    builder.adjust(1)
    return builder.as_markup()

def creation_cancel_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отменить', callback_data=CreatePostCallbackActions(action='creation_cancel')
    )
    return builder.as_markup()