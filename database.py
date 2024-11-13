from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Anime, Genre, Episode, async_session
from sqlalchemy.orm import selectinload
from typing import List, Dict
import re

async def get_session():
    async with async_session() as session:
        yield session

async def add_anime(data: dict):
    async with async_session() as session:
        try:
            # Проверка на существование аниме
            result = await session.execute(
                select(Anime).where(Anime.release_name == data['release_name'])
            )
            existing_anime = result.scalars().first()
            if existing_anime:
                print(f"Аниме с названием '{data['release_name']}' уже существует.")
                return existing_anime  # Возвращаем уже существующее аниме

            # Извлекаем количество эпизодов
            episodes_number = re.search(r'\d+', data['episodes'])
            episodes = int(episodes_number.group()) if episodes_number else 0

            # Создаём новый объект Anime
            anime = Anime(
                poster_id=data['poster_id'],
                release_name=data['release_name'],
                description=data['description'],
                episodes_count=episodes,
                dub=data['dub'],
                dub_team=data['dub_team'],
                hashtags=data['hashtags']
            )

            # Обработка жанров
            if 'genres' in data and data['genres']:
                genre_names = data['genres'].split()  # Жанры разделяются пробелом
                genres = []
                for genre_name in genre_names:
                    genre_result = await session.execute(
                        select(Genre).where(Genre.name == genre_name)
                    )
                    genre = genre_result.scalars().first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        session.add(genre)  # Добавляем новый жанр в таблицу
                    genres.append(genre)
                anime.genres = genres  # Присваиваем коллекцию жанров

            # Добавление аниме в базу данных
            session.add(anime)
            await session.commit()
            print(f"Аниме '{anime.release_name}' успешно добавлено!")
            # return anime  # Возвращаем добавленное аниме
            return True

        except Exception as exc:
            print(f"Ошибка: {exc}")
            await session.rollback()  # Откат изменений при ошибке
            raise



async def add_episodes_to_anime(anime: Anime, episode_data_list: list):
    async with async_session() as session:
        try:
            for episode_data in episode_data_list:
                episode = Episode(
                    media_id=episode_data['media_id'],
                    episode_number=episode_data['episode_number'],
                    anime_id=anime.id  # Привязываем эпизоды к аниме
                )
                session.add(episode)

            await session.commit()
            print(f"{len(episode_data_list)} эпизодов успешно добавлено к аниме '{anime.release_name}'!")

        except Exception as exc:
            print(f"Ошибка при добавлении эпизодов: {exc}")
            await session.rollback()
            raise
    


async def check_anime_exists(anime_name: str):
    async with async_session() as session:
        result = await session.execute(
            select(Anime).where(Anime.release_name == anime_name)
        )
        return result.scalars().first()




async def add_episode(anime, episode_info):
    async with async_session() as session:
        # Проверяем, есть ли уже эпизод с таким же номером для этого аниме
        existing_episode = await session.execute(
            select(Episode).filter(
                Episode.anime_id == anime.id,
                Episode.episode_number == episode_info['episode_number']
            )
        )
        existing_episode = existing_episode.scalar_one_or_none()

        if existing_episode:
            # Если эпизод уже существует
            return f"Эпизод {episode_info['episode_number']} для аниме '{anime.release_name}' уже существует в базе."

        # Если эпизод не найден, добавляем новый
        new_episode = Episode(
            media_id=episode_info['media_id'],
            episode_number=episode_info['episode_number'],
            anime_id=anime.id
        )
        session.add(new_episode)
        await session.commit()

        # Успешное добавление
        return f"Эпизод {episode_info['episode_number']} для аниме '{anime.release_name}' успешно добавлен."

# Функция для получения эпизодов для аниме по названию
async def get_episodes_for_anime(release_name: str):
    try:
        # Используем async with для работы с сессией
        async with async_session() as session:
            print(f"Поиск аниме с названием: {release_name}")

            # Выполнение запроса для поиска аниме
            result = await session.execute(
                select(Anime).where(Anime.release_name == release_name)
            )
            anime = result.scalars().first()

            if not anime:
                print(f"Аниме с названием {release_name} не найдено")
                return "Аниме не найдено."

            print(f"Аниме найдено: {anime.release_name}")

            # Извлечение эпизодов
            result = await session.execute(
                # select(Episode).where(Episode.anime_id == anime.id)
                select(Episode).where(Episode.anime_id == anime.id).order_by(Episode.episode_number) # Извлечение эпизодов, сортированных по номеру эпизода
            )
            episodes = result.scalars().all()

            if not episodes:
                print(f"Эпизоды для аниме {anime.release_name} не найдены")
                return "Эпизоды не найдены."

            return [(episode.episode_number, episode.media_id) for episode in episodes]

    except Exception as exc:
        print(f"Ошибка при извлечении серий: {exc}")
        return f"Произошла ошибка: {exc}"


# Асинхронное получение списка аниме из базы данных с их ID
async def get_anime_list() -> List[Dict]:
    async with async_session() as session:
        result = await session.execute(select(Anime.id, Anime.release_name))
        anime_list = [{"id": row[0], "name": row[1]} for row in result.fetchall()]
    return anime_list