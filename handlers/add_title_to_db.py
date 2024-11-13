from aiogram.types import Message, PhotoSize
from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from database import check_anime_exists, add_episode, add_anime
from models.models import Anime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import re

router = Router()

class AddTitleToDatabase(StatesGroup):
    get_announcement = State()


# @router.message(Command('add_title'))
# @router.message(F.photo & F.caption)
# # @router.callback_query
# async def add_title_from_announce(
#     message: types.Message,
#     state: FSMContext
#     ):
#     await message.answer(
#         'Перешли пост с анонсом.'
#     )
#     await state.set_state(AddTitleToDatabase.get_announcement)

# ОБРАБОТКА ЧЕРЕЗ СОСТОЯНИЕ

# @router.message(AddTitleToDatabase.get_announcement, F.photo & F.caption)
# async def getting_announcement(
#     message: Message,
#     state: FSMContext,
# ):
#     if message.photo:
#         poster_img = message.photo[-1]
#     else:
#         await message.answer(
#             'Не удалось найти изображение в сообщении.'
#         )

#     post = {
#         'poster_id': poster_img.file_id,
#         'message': message.caption
#     }


#     anime_data = extract_anime_data(post)
#     print(anime_data)

#     try:
#         result = await add_anime(anime_data)

#         if isinstance(result, Anime):
#             # Если аниме существует, возвращаем сообщение
#             await message.answer(
#                 f"❗️ Аниме с названием '{result.release_name}' уже существует."
#             )
#         else:
#             # Если аниме добавлено, возвращаем сообщение об успехе
#             await message.answer(f"✅ Аниме '{anime_data['release_name']}' успешно добавлено.")
#             await state.clear()

#     except Exception as exc:
#         print(exc)
#         await message.answer(
#             f'При добавлении произошла ошибка:\n\n{exc}'
#         )



#ВРЕМЕННАЯ РЕАЛИЗАЦИЯ ДЛЯ БЫСТРОГО ДОБАВЛЕНИЯ РЕЛИЗОВ В БАЗУ
@router.message(F.photo & F.caption)
async def getting_announcement(
    message: Message
    ):
    if message.photo:
        poster_img = message.photo[-1]
    else:
        await message.answer(
            'Не удалось найти изображение в сообщении.'
        )

    post = {
        'poster_id': poster_img.file_id,
        'message': message.caption
    }


    anime_data = extract_anime_data(post)
    print(anime_data)

    try:
        result = await add_anime(anime_data)

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
        await message.answer(
            f'При добавлении произошла ошибка:\n\n{exc}'
        )



def extract_anime_data(post):
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

    # 1. Извлечение названия аниме
    anime_data['release_name'] = lines[0]

    # 2. Извлечение описания
    description_end_index = next((i for i, line in enumerate(lines) if re.search(r'\d+\s+эпизод', line, re.IGNORECASE)), -1)
    anime_data['description'] = ' '.join(lines[1:description_end_index]).strip()
    
    # 3. Извлечение количества эпизодов (оставляем в виде строки)
    if description_end_index != -1:
        episodes_match = re.search(r'(\d+\s*эпизод)', lines[description_end_index], re.IGNORECASE)
        if episodes_match:
            anime_data['episodes'] = episodes_match.group(1)  # Сохраняем как строку, например, "25 эпизодов"


    # # 4. Извлечение типа и команды озвучки
    # if description_end_index + 1 < len(lines):
    #     dub_info = lines[description_end_index + 1]
    #     if ',' in dub_info:
    #         anime_data['dub'], anime_data['dub_team'] = map(str.strip, dub_info.split(',', 1))
    #     else:
    #         anime_data['dub'] = dub_info


# Маппинг для перевода типа озвучки на английский
    dub_translation = {
        "Дубляж": "dubbed",
        "Закадровая озвучка": "voiceover"
    }

    # 4. Извлечение типа и команды озвучки
    if description_end_index + 1 < len(lines):
        dub_info = lines[description_end_index + 1].strip()
        
        if ',' in dub_info:
            anime_data['dub'], anime_data['dub_team'] = map(str.strip, dub_info.split(',', 1))
        else:
            anime_data['dub'] = dub_info

        # Преобразование типа озвучки в английский формат
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
        anime_data['genres'] = ' '.join(genres)

        # Остальные хэштеги (с сохранением символа #)
        all_hashtags = ' '.join(hashtags[1:])
        anime_data['hashtags'] = all_hashtags.strip()
    
    return anime_data

