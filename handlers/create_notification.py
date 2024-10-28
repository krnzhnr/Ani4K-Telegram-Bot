from aiogram import Router, F, types, Bot
from aiogram.types import Message, PhotoSize
from keyboards.create_notification_kb import CreateNotificationCallbackActions, create_noti_release_type_selection, create_noti_channel_selection_kb, create_noti_channel_test, create_noti_finish_kb
from keyboards.menu_kb import creation_cancel_kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, StateFilter
from aiogram.methods import SendMessage, send_photo
from aiogram.utils.markdown import hide_link
import re

router = Router()

notification = {}

ADMIN_ID = 491203291


class NotificationCreation(StatesGroup):
    channel_selection = State()
    release_type_selection = State()
    add_episodes = State()
    add_name = State()
    add_caption = State()
    add_poster = State()
    add_link = State()




@router.callback_query(CreateNotificationCallbackActions.filter(F.action == 'create_notification'))
async def create_notification_channel_selection(
    callback: types.CallbackQuery,
    state: FSMContext
):
    await callback.message.edit_text(
        'Выбери канал для уведомления.',
        reply_markup=create_noti_channel_selection_kb()
    )
    await state.set_state(NotificationCreation.channel_selection)
    await callback.answer()




@router.callback_query(CreateNotificationCallbackActions.filter(F.action == 'noti_main_channel'))
async def main_channel_selected(
    callback: types.CallbackQuery,
    callback_data: CreateNotificationCallbackActions,
    state: FSMContext
):
    if callback.message.chat.id == ADMIN_ID:
        notification.update({'channel_id': '-1001995806263'})
        print(f'{callback.message.chat.full_name} выбрал канал ОСНОВНОЙ, ID = {notification['channel_id']}')
        await callback.message.edit_text(
            f'Выбран канал: <strong>Основной</strong>.\n\nВыбери тип релиза.',
            reply_markup=create_noti_release_type_selection()
        )
        await state.set_state(NotificationCreation.release_type_selection)
        await callback.answer()
    else:
        await callback.message.edit_text(
            f'Тебе, {callback.message.chat.full_name}, там делать нечего, так что давай ты выберешь <strong>тестовый</strong> и мы не будем с тобой ругаться.',
            reply_markup=create_noti_channel_test()
        )
        print(f'{callback.message.chat.full_name} пытался запостить в основу.')
        await callback.answer()




@router.callback_query(CreateNotificationCallbackActions.filter(F.action == 'noti_test_channel'))
async def test_channel_selected(
    callback: types.CallbackQuery,
    callback_data: CreateNotificationCallbackActions,
    state: FSMContext
):
    notification.update({'channel_id': '-1002303815016'})
    print(f'{callback.message.chat.full_name} выбрал канал ТЕСТОВЫЙ, ID = {notification['channel_id']}')
    await callback.message.edit_text(
        f'Выбран канал: <strong>Тестовый</strong>.\n\nВыбери тип релиза.',
        reply_markup=create_noti_release_type_selection()
    )
    await state.set_state(NotificationCreation.release_type_selection)
    await callback.answer()




@router.callback_query(CreateNotificationCallbackActions.filter(F.action == 'film_selected'))
async def create_noti_film_selected(
    callback: types.CallbackQuery,
    callback_data: CreateNotificationCallbackActions,
    state: FSMContext
):
    notification.update({'release_type': 'film'})
    print(notification)
    await callback.message.edit_text(
        'Выбранный тип релиза: <strong>Фильм</strong>\n\nПришли название фильма.',
        reply_markup=creation_cancel_kb()
    )
    await state.set_state(NotificationCreation.add_name)
    await callback.answer()




@router.message(
    NotificationCreation.add_name,
    F.text
)
async def create_noti_add_name(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    notification.update({'release_name': message.text})
    print(notification)
    await message.answer(
        'Название добавлено, теперь пришли постер.',
        reply_markup=creation_cancel_kb()
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )
    await state.set_state(NotificationCreation.add_poster)



# ПОЛУЧЕНИЕ ПОСТЕРА

@router.message(
    NotificationCreation.add_poster,
    F.photo[-1].as_('poster_img')
)
async def create_noti_add_poster(
    message: Message,
    state: FSMContext,
    poster_img: PhotoSize,
    bot: Bot
):
    notification.update({'poster_id': poster_img.file_id})
    print(f'ID постера: {notification['poster_id']}')
    print(notification)
    await message.answer(
        text='Постер добавлен, дальше пришли ссылку на сообщение с фильмом.',
        reply_markup=creation_cancel_kb()
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )
    await state.set_state(NotificationCreation.add_link)




@router.message(
    NotificationCreation.add_link,
    F.text
)
async def create_noti_get_link(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    link = {
        'url': 'N/A'
    }
    entities = message.entities or []
    for item in entities:
        if item.type in link.keys():
            link['url'] = item.extract_from(message.text)
    notification.update({'link': link['url']})

    await message.answer(
        'Ссылка добавлена.\n\nИтоговый вид уведомления:'
    )
    await message.answer(
        f'{hide_link({notification['poster_id']})}Полнометражный фильм {notification['release_name']} доступен для просмотра!',
        reply_markup=create_noti_finish_kb()
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )

    print(notification)
    await state.clear()