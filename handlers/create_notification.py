from aiogram import Router, F, types, Bot
from aiogram.types import Message, PhotoSize
from keyboards.create_notification_kb import CreateNotificationCallbackActions, create_noti_release_type_selection, create_noti_channel_selection_kb, create_noti_channel_test, create_noti_finish_kb, create_noti_howmuchepisedes_selection_kb
from keyboards.menu_kb import creation_cancel_kb, menu_kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, StateFilter
from aiogram.methods import SendMessage, send_photo
from aiogram.utils.markdown import hide_link
from catbox import CatboxUploader
from database import check_anime_exists, add_episode
import re

router = Router()

uploader = CatboxUploader()

notification = {}

ADMIN_ID = 491203291
CHAT_ID = '-1002104882531'  # ID чата



class NotificationCreation(StatesGroup):
    channel_selection = State()
    release_type_selection = State()
    # howMuchEpisodes_selection = State()
    add_episodes = State()
    add_name = State()
    add_caption = State()
    add_poster = State()
    add_link = State()




@router.message(F.video & F.caption)
async def handle_video_message(message: Message, bot: Bot):
    # Извлекаем ID видео и подпись
    video_id = message.video.file_id
    caption = message.caption

    if not caption:
        await message.answer("Отправьте видео с подписью.")
        return

    # Извлекаем информацию из подписи
    episode_info = extract_episode_info(caption)
    episode_info['media_id'] = video_id
    print(f"Extracted info: {episode_info}")

    anime_name = episode_info.get('anime_name')
    if not anime_name:
        await message.answer("Не удалось извлечь название аниме из подписи.")
        return

    # Проверка наличия аниме в базе
    anime = await check_anime_exists(anime_name)
    if anime:
        await add_episode(anime, episode_info)
        await message.answer(f"Эпизод {episode_info['episode_number']} для '{anime_name}' успешно добавлен.")
    else:
        await message.answer(f"Аниме '{anime_name}' не найдено в базе. Сначала добавьте его.")

      


def extract_episode_info(caption: str):
    # Шаблон для извлечения названия аниме до первого номера эпизода
    anime_name_pattern = r"^\[?\d*\]?\s*(.*?)\s*(?=\d+\s*эпизод)"  # Теперь \[?\d*\]? — необязательные скобки
    # Шаблон для номера эпизода
    episode_pattern = r"(\d+)\s*эпизод"
    # Шаблон для типа озвучки (дубляж или закадровая озвучка)
    dub_pattern = r"(дубляж|закадровая озвучка)"
    # Шаблон для команды озвучки (после запятой)
    team_pattern = r",\s*([^\n#]+)"  # Текст после запятой до конца строки или до хештега

    # Извлекаем название аниме
    anime_name = re.search(anime_name_pattern, caption, flags=re.DOTALL)
    # Извлекаем номер эпизода
    episode = re.search(episode_pattern, caption)
    # Извлекаем тип озвучки
    dub = re.search(dub_pattern, caption, flags=re.IGNORECASE)
    # Извлекаем команду озвучки
    team = re.search(team_pattern, caption)

    return {
        "anime_name": anime_name.group(1).strip() if anime_name else None,
        "episode_number": int(episode.group(1)) if episode else None,
        "dub": dub.group(1).strip().capitalize() if dub else None,
        "team": team.group(1).strip() if team else None
    }




# ОТПРАВКА ВЫБОРА КАНАЛА

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




# ВЫБОР КАНАЛА

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




# ВЫБОР ТИПА РЕЛИЗА

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




# ПОЛУЧЕНИЕ ТИПА РЕЛИЗА: ФИЛЬМ

@router.callback_query(CreateNotificationCallbackActions.filter(F.action == 'film_selected'))
async def create_noti_film_selected(
    callback: types.CallbackQuery,
    callback_data: CreateNotificationCallbackActions,
    state: FSMContext
):
    notification.update({'release_type': 'film'})
    print(f'Выбранный тип релиза: Фильм')
    await callback.message.edit_text(
        'Выбранный тип релиза: <strong>Фильм</strong>\n\nПришли название фильма.',
        reply_markup=creation_cancel_kb()
    )
    await state.set_state(NotificationCreation.add_name)
    await callback.answer()




# ПОЛУЧЕНИЕ ТИПА РЕЛИЗА: СЕРИАЛ

@router.callback_query(CreateNotificationCallbackActions.filter(F.action == 'series_selected'))
async def create_noti_film_selected(
    callback: types.CallbackQuery,
    callback_data: CreateNotificationCallbackActions,
    state: FSMContext
):
    notification.update({'release_type': 'series'})
    print(f'Выбранный тип релиза: Сериал')
    await callback.message.edit_text(
        'Выбранный тип релиза: <strong>Сериал</strong>\n\nВыбери, сколько эпизодов стало доступно.',
        reply_markup=create_noti_howmuchepisedes_selection_kb()
    )
    # await state.set_state(NotificationCreation.howMuchEpisodes_selection)
    await callback.answer()




# ВЫБРАН ОДИН ЭПИЗОД

@router.callback_query(CreateNotificationCallbackActions.filter(F.action == 'one_episode_selected'))
async def create_noti_one_episode_selected(
    callback: types.CallbackQuery,
    callback_data: CreateNotificationCallbackActions,
    state: FSMContext
):
    notification.update({'how_many_episodes': 'one'})
    print(f'Количество эпизодов: Один')
    await callback.message.edit_text(
        f'Стало доступно эпизодов: <strong>Один</strong>\n\nПришли номер этого эпизода.',
        reply_markup=creation_cancel_kb()
    )
    await state.set_state(NotificationCreation.add_episodes)
    await callback.answer()




# ВЫБРАНО НЕСКОЛЬКО ЭПИЗОДОВ

@router.callback_query(CreateNotificationCallbackActions.filter(F.action == 'many_episodes_selected'))
async def create_noti_many_episodes_selected(
    callback: types.CallbackQuery,
    callback_data: CreateNotificationCallbackActions,
    state: FSMContext
):
    notification.update({'how_many_episodes': 'many'})
    print(f'Количество эпизодов: Несколько')
    await callback.message.edit_text(
        f'Стало доступно эпизодов: <strong>Несколько</strong>\n\nПришли номер первого и последнего эпизода через дефиз.\n\nНапример: 1-5',
        reply_markup=creation_cancel_kb()
    )
    await state.set_state(NotificationCreation.add_episodes)
    await callback.answer()




# ПОЛУЧЕНИЕ НОМЕРА ЭПИЗОДА / ЭПИЗОДОВ

@router.message(
        NotificationCreation.add_episodes,
        F.text
)
async def get_episodes(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    if notification['how_many_episodes'] == 'one':
        notification.update({'episode': message.text})
        print(f'Номер эпизода: {message.text}')
        await message.answer(
            'Номер эпизода добавлен, теперь пришли название сериала.',
            reply_markup=creation_cancel_kb()
        )
    elif notification['how_many_episodes'] == 'many':
        notification.update({'episodes': message.text})
        print(f'Номера эпизодов: {message.text}')
        await message.answer(
            'Номера эпизодов добавлены, теперь пришли название сериала.',
            reply_markup=creation_cancel_kb()
        )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )
    await state.set_state(NotificationCreation.add_name)




# ПОЛУЧЕНИЕ НАЗВАНИЯ

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
    print(f'Название сериала/фильма: {message.text}')
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
    uploading_message = await message.answer(
        'Загружаю постер, ожидайте...'
    )

    await bot.send_chat_action(
        chat_id=message.chat.id,
        action='upload_photo'
        )

    # СКАЧИВАНИЕ И ПОЛУЧЕНИЕ ССЫЛКИ НА ФОТО

    img = await bot.get_file(poster_img.file_id)
    img_path = img.file_path
    await bot.download_file(img_path, f'img/{poster_img.file_id}.jpg')

    poster_link = uploader.upload_file(f'img/{poster_img.file_id}.jpg')

    notification.update({'link': poster_link})

    await uploading_message.edit_text(
        'Постер добавлен.\n\nИтоговый вид уведомления:'
    )

    await message.answer(
        notification_text_assembly(),
        reply_markup=create_noti_finish_kb()
    )

    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )
    await state.clear()




# ПОДБОР ТЕКСТА УВЕДОМЛЕНИЯ

def notification_text_assembly():
    if notification['release_type'] == 'film':
        notification_text = f'{hide_link(notification['link'])}Полнометражный фильм «{notification["release_name"]}» доступен для просмотра!'
        print(f'Текст готового уведомления: {notification_text}')
        return notification_text
    
    elif notification['release_type'] == 'series':
        if notification['how_many_episodes'] == 'one':
            notification_text = f'{hide_link(notification['link'])}{notification['episode']}-й эпизод сериала «{notification["release_name"]}» доступен для просмотра!'
            print(f'Текст готового уведомления: {notification_text}')
            return notification_text
        
        elif notification['how_many_episodes'] == 'many':
            notification_text = f'{hide_link(notification['link'])}{notification['episodes']} эпизоды сериала «{notification["release_name"]}» доступны для просмотра!'
            print(f'Текст готового уведомления: {notification_text}')
            return notification_text
            



# ОБРАБОТКА ПУБЛИКАЦИИ

@router.callback_query(CreateNotificationCallbackActions.filter(F.action == 'noti_publish'))
async def post_publish(
    callback: types.CallbackQuery,
    callback_data: CreateNotificationCallbackActions,
    bot: Bot
):
    try:
        sent_message = await bot.send_message(
            chat_id=notification['channel_id'],
            text=notification_text_assembly()
        )
        await callback.message.answer(
            text='Уведомление опубликовано, перед тобой меню.',
            reply_markup=menu_kb()
        )
        print(f'Уведомление опубликовано.')
        await bot.delete_messages(
            callback.message.chat.id,
            [callback.message.message_id, callback.message.message_id - 1]
        )
        if notification['channel_id'] == '-1002303815016':
            pass
        else:
            await bot.forward_message(
                chat_id=CHAT_ID,
                from_chat_id=notification['channel_id'],
                message_id=sent_message.message_id
            )
        print(notification)
        notification.clear()
        await callback.answer()
    except Exception as exc:
        print(exc)
        await callback.message.edit_text(
            text=f'Что-то пошло не так, вот причина:\n\n{exc}'
        )
        await callback.answer()




# ОБРАБОТКА ОТМЕНЫ ГОТОВОГО ПОСТА

@router.callback_query(CreateNotificationCallbackActions.filter(F.action == 'noti_finish_cancel'))
async def post_cancel(
    callback: types.CallbackQuery,
    callback_data: CreateNotificationCallbackActions,
    state: FSMContext,
    bot: Bot
):
    await state.clear()
    notification.clear()
    await callback.message.answer(
        text='Уведомление удалено, перед тобой меню.',
        reply_markup=menu_kb()
    )
    await bot.delete_messages(
        callback.message.chat.id,
        [callback.message.message_id, callback.message.message_id - 1]
    )
    await callback.answer()
