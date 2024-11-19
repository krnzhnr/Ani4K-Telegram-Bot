import re
from aiogram import Router, F, types, Bot
from aiogram.types import Message, PhotoSize
from aiogram.filters import Command
from database import check_anime_exists, add_episode, add_anime  # Локальные импорты для работы с базой данных
from models.models import Anime  # Локальный импорт модели Anime
from aiogram.fsm.context import FSMContext  # Локальный импорт для работы с состояниями FSM
from aiogram.fsm.state import StatesGroup, State  # Локальные импорты для состояний FSM

router = Router()

class AddTitleToDatabase(StatesGroup):
    get_announcement = State()  # Определение состояния для получения анонса


# -------------------------------------------
# Закомментированный код для обработки команд и сообщений:

# @router.message(Command('add_title'))
# @router.message(F.photo & F.caption)
# # @router.callback_query
# async def add_title_from_announce(
#     message: types.Message,
#     state: FSMContext
# ):
#     """
#     Обработчик для команды '/add_title'.
#     Ожидает пересланное сообщение с анонсом.
#     """
#     await message.answer('Перешли пост с анонсом.')
#     await state.set_state(AddTitleToDatabase.get_announcement)


# ОБРАБОТКА ЧЕРЕЗ СОСТОЯНИЕ:

# @router.message(AddTitleToDatabase.get_announcement, F.photo & F.caption)
# async def getting_announcement(
#     message: Message,
#     state: FSMContext
# ):
#     """
#     Обработка сообщения с фото и подписью при активном состоянии.
#     Извлекает данные из сообщения и добавляет аниме в базу данных.
#     """
#     if message.photo:
#         poster_img = message.photo[-1]  # Получаем самое большое изображение
#     else:
#         await message.answer('Не удалось найти изображение в сообщении.')
#         return

#     post = {
#         'poster_id': poster_img.file_id,
#         'message': message.caption
#     }

#     anime_data = extract_anime_data(post)
#     print(anime_data)

#     try:
#         result = await add_anime(anime_data)

#         if isinstance(result, Anime):
#             # Если аниме уже существует
#             await message.answer(
#                 f"❗️ Аниме с названием '{result.release_name}' уже существует."
#             )
#         else:
#             # Успешное добавление аниме
#             await message.answer(f"✅ Аниме '{anime_data['release_name']}' успешно добавлено.")
#             await state.clear()

#     except Exception as exc:
#         print(exc)
#         await message.answer(f'При добавлении произошла ошибка:\n\n{exc}')

# -------------------------------------------


# Временная реализация для быстрого добавления релизов в базу
@router.message(F.photo & F.caption)
async def getting_announcement(message: Message):
    """
    Обработка сообщений с изображением и подписью.
    Извлекаем данные и добавляем аниме в базу.
    """
    if message.photo:
        poster_img = message.photo[-1]  # Получаем самое большое изображение
    else:
        await message.answer('Не удалось найти изображение в сообщении.')
        return

    post = {
        'poster_id': poster_img.file_id,
        'message': message.caption
    }

    anime_data = extract_anime_data(post)  # Извлекаем данные о аниме
    print(anime_data)

    try:
        result = await add_anime(anime_data)  # Добавляем аниме в базу данных

        if isinstance(result, Anime):
            # Если аниме существует, возвращаем сообщение
            await message.answer(
                f"❗️ Аниме с названием '{result.release_name}' уже существует."
            )
        else:
            # Если аниме добавлено, возвращаем сообщение об успехе
            await message.answer(f"✅ Аниме '{anime_data['release_name']}' успешно добавлено.")
    except Exception as exc:
        print(exc)
        await message.answer(f'При добавлении произошла ошибка:\n\n{exc}')


def extract_anime_data(post):
    """
    Извлекает данные о названии аниме, описании, эпизодах, озвучке и жанрах из подписи.
    """
    message = post['message']
    lines = message.splitlines()
    
    # Удаляем пустые строки
    lines = [line.strip() for line in lines if line.strip()]

    # Инициализация переменных
    anime_data = {
        'poster_id': post['poster_id'],
        'release_name': '',
        'description': '',
        'episodes': 0,
        'dub': '',
        'dub_team': '',
        'genres': '',
        'hashtags': ''
    }

    # 1. Извлечение названия аниме (первое слово/строка)
    anime_data['release_name'] = lines[0]

    # 2. Извлечение описания до строки с номером эпизода
    description_end_index = next(
        (i for i, line in enumerate(lines) if re.search(r'\d+\s*(эпизод|серия)', line, re.IGNORECASE)), -1
    )
    anime_data['description'] = ' '.join(lines[1:description_end_index]).strip()
    
    # 3. Извлечение количества эпизодов или серий с использованием регулярного выражения
    if description_end_index != -1:
        episodes_match = re.search(r'\b(\d+)\s*(сери\w*|эпизод\w*)\b', lines[description_end_index], re.IGNORECASE)
        if episodes_match:
            anime_data['episodes'] = int(episodes_match.group(1))  # Сохраняем как целое число
        else:
            anime_data['episodes'] = 0

    # Маппинг для перевода типа озвучки на английский
    dub_translation = {
        "Дубляж": "dubbed",
        "Закадровая озвучка": "voiceover"
    }

    # 4. Извлечение типа озвучки и команды
    if description_end_index + 1 < len(lines):
        dub_info = lines[description_end_index + 1].strip()
        
        # Если в строке есть запятая, разделяем на тип озвучки и команду
        if ',' in dub_info:
            anime_data['dub'], anime_data['dub_team'] = map(str.strip, dub_info.split(',', 1))
        else:
            anime_data['dub'] = dub_info

        # Преобразование типа озвучки на английский формат
        if "озвучка" in anime_data['dub'].lower():
            anime_data['dub'] = "voiceover"
        elif anime_data['dub'] in dub_translation:
            anime_data['dub'] = dub_translation[anime_data['dub']]

    # 5. Извлечение жанров и хэштегов
    hashtags = [line for line in lines if line.startswith('#')]
    
    if hashtags:
        genres_line = hashtags[0]
        # Жанры: все слова после первого хэштега до следующего хэштега
        genres = re.findall(r'#(\w+)', genres_line)
        # Преобразуем жанры в формат Title Case
        anime_data['genres'] = ' '.join(genre.title() for genre in genres)

        # Остальные хэштеги (с сохранением символа #)
        all_hashtags = ' '.join(hashtags[1:])
        anime_data['hashtags'] = all_hashtags.strip()
    
    return anime_data
