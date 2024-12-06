from aiogram import Router, F, types, Bot
from aiogram.types import Message, ReplyKeyboardRemove, PhotoSize
from keyboards.menu_kb import menu_kb, creation_cancel_kb
from keyboards.create_post_kb import (
    choice_dub_kb, create_post_finish_kb,
    create_post_channel_selection_kb, create_post_channel_test,
    CreatePostCallbackActions, ChoiceDubCallbackActions
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, StateFilter
from database import add_anime
import re

# Инициализация роутера и глобальных переменных
router = Router()
post = {}

ADMIN_ID = 491203291
CHAT_ID = '-1002104882531'  # ID чата
SOURCE_CHAT_ID = '-1002189764703'
MAIN_CHANNEL_ID = '-1001995806263'
TEST_CHANNEL_ID = '-1002303815016'


# ================== СОСТОЯНИЯ ДЛЯ СОЗДАНИЯ ПОСТА ==================

class PostCreation(StatesGroup):
    """
    Состояния для процесса создания поста.
    """
    channel_selection = State()
    add_poster = State()
    add_name = State()
    add_description = State()
    add_episodes = State()
    add_dub = State()
    add_genres_and_topics = State()


# ============ ВЫБОР КАНАЛА ДЛЯ СОЗДАНИЯ ПОСТА ============

@router.callback_query(CreatePostCallbackActions.filter(F.action == 'create_announcement'))
async def create_post_channel_selection(callback: types.CallbackQuery, callback_data: CreatePostCallbackActions, state: FSMContext):
    """
    Начало создания поста: выбор канала для публикации.
    """
    await callback.message.edit_text('Выбери канал для поста.', reply_markup=create_post_channel_selection_kb())
    await state.set_state(PostCreation.channel_selection)
    await callback.answer()


# ============ ВЫБОР ОСНОВНОГО КАНАЛА ============

@router.callback_query(CreatePostCallbackActions.filter(F.action == 'main_channel'))
async def main_channel_selected(callback: types.CallbackQuery, callback_data: CreatePostCallbackActions, state: FSMContext):
    """
    Выбор основного канала.
    """
    if callback.message.chat.id == ADMIN_ID:
        post.update({'channel_id': '-1001995806263'})
        print(f'{callback.message.chat.full_name} выбрал канал ОСНОВНОЙ, ID = {post["channel_id"]}')
        await callback.message.edit_text(
            'Выбран канал: <strong>Основной</strong>.\n\nПришли мне постер.',
            reply_markup=creation_cancel_kb()
        )
        await state.set_state(PostCreation.add_poster)
    else:
        await callback.message.edit_text(
            f'Тебе, {callback.message.chat.full_name}, там делать нечего, так что давай ты выберешь <strong>тестовый</strong> и мы не будем с тобой ругаться.',
            reply_markup=create_post_channel_test()
        )
        print(f'{callback.message.chat.full_name} пытался запостить в основной канал.')
    await callback.answer()


# ============ ВЫБОР ТЕСТОВОГО КАНАЛА ============

@router.callback_query(CreatePostCallbackActions.filter(F.action == 'test_channel'))
async def test_channel_selected(callback: types.CallbackQuery, callback_data: CreatePostCallbackActions, state: FSMContext):
    """
    Выбор тестового канала.
    """
    post.update({'channel_id': '-1002303815016'})
    print(f'{callback.message.chat.full_name} выбрал канал ТЕСТОВЫЙ, ID = {post["channel_id"]}')
    await callback.message.edit_text(
        'Выбран канал: <strong>Тестовый</strong>.\n\nПришли мне постер.',
        reply_markup=creation_cancel_kb()
    )
    await state.set_state(PostCreation.add_poster)
    await callback.answer()


# ============ ПОЛУЧЕНИЕ ПОСТЕРА ============

@router.message(PostCreation.add_poster, F.photo[-1].as_('poster_img'))
async def add_poster(message: Message, state: FSMContext, poster_img: PhotoSize, bot: Bot):
    """
    Получение постера и сохранение его ID.
    """
    post.update({'poster_id': poster_img.file_id})
    print(f'ID постера: {post["poster_id"]}')
    await message.answer(
        text='Постер добавлен, дальше пришли полное название с Шикимори.',
        reply_markup=creation_cancel_kb()
    )
    await bot.delete_messages(message.chat.id, [message.message_id, message.message_id - 1])
    await state.set_state(PostCreation.add_name)


# ============ ПОЛУЧЕНИЕ НАЗВАНИЯ ============

@router.message(PostCreation.add_name, F.text)
async def add_name(message: Message, state: FSMContext, bot: Bot):
    """
    Получение названия сериала/фильма.
    """
    post.update({'release_name': message.text})
    print(f'Название: {post["release_name"]}')
    await message.answer(
        text='Название добавлено, теперь пришли описание (не длиннее 750 символов).',
        reply_markup=creation_cancel_kb()
    )
    await bot.delete_messages(message.chat.id, [message.message_id, message.message_id - 1])
    await state.set_state(PostCreation.add_description)


# ============ ПОЛУЧЕНИЕ ОПИСАНИЯ ============

@router.message(PostCreation.add_description, F.text)
async def add_description(message: Message, state: FSMContext, bot: Bot):
    """
    Получение описания и проверка его длины.
    """
    if len(message.text) < 750:
        post.update({'description': message.text})
        print(f'Описание: {post["description"]}')
        await message.answer(
            text='Описание добавлено, теперь укажи количество эпизодов в формате "[Количество] эпизодов(-да)".',
            reply_markup=creation_cancel_kb()
        )
        await bot.delete_messages(
            message.chat.id,
            [message.message_id, message.message_id - 1]
        )
        await state.set_state(PostCreation.add_episodes)
    else:
        await message.answer(
            text=f'Текст слишком длинный ({len(message.text)} символов), необходимо не более 750. Попробуй снова.',
            reply_markup=creation_cancel_kb()
        )
    await bot.delete_messages(message.chat.id, [message.message_id, message.message_id - 1])


# ============ ПОЛУЧЕНИЕ КОЛИЧЕСТВА ЭПИЗОДОВ ============

@router.message(PostCreation.add_episodes, F.text)
async def add_episodes(message: Message, state: FSMContext, bot: Bot):
    """
    Получение количества эпизодов.
    """
    post.update({'episodes': message.text})
    print(f'Количество эпизодов: {post["episodes"]}')
    await message.answer(
        text='Количество эпизодов добавлено, выбери тип озвучки:',
        reply_markup=choice_dub_kb()
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )


# ============ ОБРАБОТКА НАЖАТИЯ КНОПКИ "ДУБЛИРОВАННЫЙ" ============
@router.callback_query(ChoiceDubCallbackActions.filter(F.dub == 'dubbed'))
async def dub_callback(
    callback: types.CallbackQuery,
    callback_data: ChoiceDubCallbackActions,
    state: FSMContext
):
    """
    Если выбран тип озвучки "Дублированный"
    """
    post.update({'dub': 'dubbed'})
    print(f'Тип озвучки: {post['dub']}')
    dub_type = post['dub']
    await callback.message.edit_text(
        f'Выбранный тип озвучки: <strong>Дубляж</strong>\n\nПришли название команды.',
        reply_markup=creation_cancel_kb()
    )
    await state.set_state(PostCreation.add_dub)
    await callback.answer(
        text=dub_type,
        show_alert=False
    )


# ============ ОБРАБОТКА НАЖАТИЯ КНОПКИ "ЗАКАДРОВАЯ" ============

@router.callback_query(ChoiceDubCallbackActions.filter(F.dub == 'voiceover'))
async def voiceover_callback(
    callback: types.CallbackQuery,
    callback_data: ChoiceDubCallbackActions,
    state: FSMContext
):
    """
    Если выбран тип озвучки "Закадровая озвучка"
    """
    post.update({'dub': 'voiceover'})
    print(f'Тип озвучки: {post['dub']}')
    dub_type = post['dub']
    await callback.message.edit_text(
        f'Выбранный тип озвучки: <strong>Закадровая озвучка</strong>\n\nПришли название команды.',
        reply_markup=creation_cancel_kb()
    )
    await state.set_state(PostCreation.add_dub)
    await callback.answer(
        text=dub_type,
        show_alert=False
    )


# ============ ВВОД НАЗВАНИЯ КОМАНДЫ ОЗВУЧКИ ============

@router.message(
    PostCreation.add_dub,
    F.text
)
async def add_dub(message: Message, state: FSMContext, bot: Bot):
    """
    Функция получения команды озвучки от пользователя.
    """
    post.update({'dub_team': message.text})
    print(f'Команда озвучки: {post['dub_team']}')
    # await message.answer(str(post))
    await message.answer(
        text='Тип озвучки и команда добавлены, теперь пришли жанры и темы с Шикимори через пробел.',
        reply_markup=creation_cancel_kb()
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )
    await state.set_state(PostCreation.add_genres_and_topics)


# ============ ВВОД ЖАНРОВ И ТЕМ + ЗАВЕРШЕНИЕ РАБОТЫ КОНЕЧНОГО АВТОМАТА ============

@router.message(
    PostCreation.add_genres_and_topics,
    F.text
)
async def add_genres_and_topics(message: Message, state: FSMContext, bot: Bot):
    """
    В функции получаем сообщение с жанрами через пробел.
    - genres_and_topics будет использоваться для хэштегов в анонсе,
    - genres будет использоваться без хэштегов для последующего
    разделения по пробелу и записи в БД.
    """
    genres_and_topics_list = message.text.split()
    topics_list = ''
    genres_str = ''

    # Формируем строку с хэштегами и строку жанров с заглавными буквами
    for topic in genres_and_topics_list:
        updated_topic = '#' + topic + ' '
        topics_list += updated_topic.title()
        genres_str += topic.title() + ' '

    # Сохраняем в словарь
    post.update({
        'genres_and_topics': topics_list.strip(),  # строка с хэштегами
        'genres': genres_str.strip()  # строка жанров с заглавными буквами без хэштегов для БД
    })
    print(f'Жанры и темы: {post['genres_and_topics']}')
    await message.answer(
        text=f'Жанры и темы добавлены.\n\nВот итоговый вид поста:'
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )
    create_final_hashtags()  # Запускаем функцию, которая соберет строку с хэштегами #НАЗВАНИЕ #КОМАНДА_ОЗВУЧКИ
    await state.clear()
    try:
        await message.answer_photo(
            photo=post['poster_id'],
            caption=post_assembly(),
            reply_markup=create_post_finish_kb()
        )
        print(f'\n{message.from_user.full_name} собрал пост:\n\n{post}')
    except Exception as exc:
        await message.answer(str(exc))


# ============ СБОРКА ХЭШТЕГОВ ============

def create_final_hashtags():
    """
    Функция собирает строку с хэштегами #НАЗВАНИЕ #КОМАНДА_ОЗВУЧКИ
    """
    name_hashtag = ''
    dub_team_hashtag = ''

    # Извлечение названия аниме и создание хэштега
    release_name = post['release_name']
    release_name = release_name.split('/')[0]
    release_name = re.sub(r'[^\w\s]', '', release_name)
    release_name = release_name.replace(' ', '_')
    release_name = release_name.strip('_')
    name_hashtag = f'#{release_name}'

    # Получение и форматирование команды озвучки с последующим созданием хэштегом
    dub_team = post['dub_team']
    dub_team = re.sub(r'[^\w\s/-]', '', dub_team)
    dub_team = re.sub(r'[\s/-]+', '_', dub_team)
    dub_team_hashtag = f'#{dub_team}'

    # Объединение вышесозданных хэштегов в строку и ее запись в словарь для публикации
    final_hashtags = f'{name_hashtag} {dub_team_hashtag}'
    post.update({'hashtags': final_hashtags})
    print(post['hashtags'])


# ============ СБОРКА ПОСТА ============

def post_assembly():
    """
    Сборка полного текста поста для отправки.
    Включает все данные о названии, описании, эпизодах, типе озвучки, жанрах и хэштегах.
    """
    dub_type = 'Дубляж,' if post['dub'] == 'dubbed' else 'Закадровая озвучка,'
    ready_post = (f'<b><u>{post["release_name"]}</u></b>\n\n<i><blockquote expandable>{post["description"]}</blockquote></i>\n\n'
                f'{post["episodes"]}\n\n{dub_type} {post["dub_team"]}\n\n{post["genres_and_topics"]}\n\n{post["hashtags"]}')
    return ready_post


# ============ ОБРАБОТКА ПУБЛИКАЦИИ ============

@router.callback_query(CreatePostCallbackActions.filter(F.action == 'publish'))
async def post_publish(
    callback: types.CallbackQuery,
    callback_data: CreatePostCallbackActions,
    bot: Bot
):
    """
    Обработка публикации поста.
    Сохраняем данные в базе, отправляем пост в канал,
    создаем топик, закрываем его, и отправляем анонс в топик.
    """
    try:
        anime_data = {
            'poster_id': post['poster_id'],
            'release_name': post['release_name'],
            'description': post['description'],
            'episodes': post['episodes'],
            'dub': post['dub'],
            'dub_team': post['dub_team'],
            'genres': post['genres'],
            'hashtags': post['hashtags']
        }
        print(f'Data in create_post: {anime_data}')

        # Сохраняем данные в базу
        if callback.message.chat.id == ADMIN_ID and post['channel_id'] == MAIN_CHANNEL_ID:
            await add_anime(anime_data)
        else:
            print(f'Пропущена запись в базу, запостил {callback.message.chat.full_name}')
            pass

        # Подготовим текст поста один раз
        post_caption = post_assembly()

        # Отправляем фото и пост в канал
        sent_message = await bot.send_photo(
            chat_id=post['channel_id'],
            photo=post['poster_id'],
            caption=post_caption
        )

        # Удаляем сообщения из чата
        await callback.message.answer(
            text='Пост опубликован, перед тобой меню.',
            reply_markup=menu_kb()
        )
        await bot.delete_messages(
            callback.message.chat.id,
            [callback.message.message_id, callback.message.message_id - 1]
        )

        if post['channel_id'] != '-1002303815016':
            # Пересылаем сообщение в основной чат
            await bot.forward_message(
                chat_id=CHAT_ID,
                from_chat_id=post['channel_id'],
                message_id=sent_message.message_id
            )

            # Создаём топик в Ani4K HUB
            topic = await bot.create_forum_topic(
                chat_id=CHAT_ID,
                name=post['release_name'].split('/')[0].strip()
            )

            # Закрываем топик для сообщений пользователей
            await bot.close_forum_topic(
                chat_id=CHAT_ID,
                message_thread_id=topic.message_thread_id
            )

            # Отправляем фото в топик
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=post['poster_id'],
                caption=post_caption,  # Используем уже подготовленный текст
                message_thread_id=topic.message_thread_id  # ID топика
            )
            
            # Создаём топик в Ani4K Source
            source_topic = await bot.create_forum_topic(
                chat_id=SOURCE_CHAT_ID,
                name=post['release_name'].split('/')[0].strip()
            )
            
            # Отправляем фото в топик
            await bot.send_photo(
                chat_id=SOURCE_CHAT_ID,
                photo=post['poster_id'],
                caption=post_caption,  # Используем уже подготовленный текст
                message_thread_id=source_topic.message_thread_id  # ID топика
            )

        post.clear()
        await callback.answer()

    except Exception as exc:
        print(exc)
        await callback.message.answer(
            text=f'Что-то пошло не так, вот причина:\n\n{exc}'
        )
        await callback.answer()


# ============ ОБРАБОТКА ОТМЕНЫ ГОТОВОГО ПОСТА ============

@router.callback_query(CreatePostCallbackActions.filter(F.action == 'finish_cancel'))
async def post_cancel(
    callback: types.CallbackQuery,
    callback_data: CreatePostCallbackActions,
    state: FSMContext,
    bot: Bot
):
    """
    Отмена создания поста на странице просмотра поста перед публикацией по кнопке "Отменить"
    """
    await state.clear()
    post.clear()
    await callback.message.answer(
        text='Пост удален, можно создавать новый.',
        reply_markup=menu_kb()
    )
    await bot.delete_messages(
        callback.message.chat.id,
        [callback.message.message_id, callback.message.message_id - 1]
    )
    await callback.answer()


# ============ ОБРАБОТКА ОТМЕНЫ В ПРОЦЕССЕ СОЗДАНИЯ ============

@router.callback_query(CreatePostCallbackActions.filter(F.action == 'creation_cancel'))
async def creation_cancel(
    callback: types.CallbackQuery,
    callback_data: CreatePostCallbackActions,
    state: FSMContext,
    bot: Bot
):
    """
    Отмена создания поста на любом этапе создания поста по кнопке "Отменить"
    """

    await state.clear()
    post.clear()
    await callback.message.answer(
        text='Создание поста отменено, перед тобой меню.',
        reply_markup=menu_kb()
    )
    await bot.delete_messages(
        callback.message.chat.id,
        [callback.message.message_id, callback.message.message_id - 1]
    )
    await callback.answer()


