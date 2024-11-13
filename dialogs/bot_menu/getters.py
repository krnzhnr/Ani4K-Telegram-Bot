from sqlalchemy.future import select
from sqlalchemy import func
from aiogram_dialog import DialogManager
from typing import Dict, List
from models.models import Anime, Episode, async_session

# Объединённая функция: получение данных и подготовка для использования в диалоге
# async def get_anime_data(dialog_manager: DialogManager, **kwargs) -> Dict:
#     async with async_session() as session:
#         # Запрос данных из базы
#         result = await session.execute(select(Anime.id, Anime.release_name))
#         # Разделяем название аниме на часть до знака "/"
#         anime_list = [{"id": row[0], "name": row[1].split('/')[0]} for row in result.fetchall()]
    
#     # Возвращаем словарь с обновленными данными
#     return {"anime_list": anime_list}


async def get_anime_data(dialog_manager: DialogManager, **kwargs) -> Dict:
    async with async_session() as session:
        # Запрос на получение аниме с количеством всех эпизодов
        result = await session.execute(
            select(Anime.id, Anime.release_name, Anime.episodes_count)
            .join(Episode, Episode.anime_id == Anime.id, isouter=True)
            .group_by(Anime.id)
        )

        anime_list = []
        for row in result.fetchall():
            anime_id = row[0]
            # Подсчитываем количество доступных эпизодов (например, просто количество эпизодов)
            available_episodes = await session.execute(
                select(func.count(Episode.id)).filter(Episode.anime_id == anime_id)
            )
            available_episodes_count = available_episodes.scalar()

            # Добавляем в список
            anime_list.append({
                "id": row[0],
                "name": row[1],
                "episodes_count": row[2],  # Общее количество эпизодов из Anime
                "available_episodes": available_episodes_count  # Доступные эпизоды
            })
        
    return {"anime_list": anime_list}


