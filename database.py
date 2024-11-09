from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Anime, Genre, async_session
import re

async def add_anime_from_dict(data: dict):
    async with async_session() as session:
        try:
            # Проверка на существование аниме по названию
            result = await session.execute(
                select(Anime).where(Anime.release_name == data['release_name'])
            )
            existing_anime = result.scalars().first()
            if existing_anime:
                print("Аниме с таким названием уже существует.")
                return

            # Извлекаем только число из строки 'episodes'
            episodes_number = re.search(r'\d+', data['episodes'])
            episodes = episodes_number.group() if episodes_number else '0'

            # Создаем новый объект Anime
            anime = Anime(
                poster_id=data['poster_id'],
                release_name=data['release_name'],
                description=data['description'],
                episodes=episodes,  # Сохраняем только число
                dub=data['dub'],
                dub_team=data['dub_team'],
                hashtags=data['hashtags']
            )
            
            print(f"Извлечено количество эпизодов: {episodes}")

            # Обработка жанров
            if 'genres' in data and data['genres']:
                genre_names = data['genres'].split()
                genres = []
                for genre_name in genre_names:
                    genre_result = await session.execute(
                        select(Genre).where(Genre.name == genre_name)
                    )
                    genre = genre_result.scalars().first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        session.add(genre)
                    genres.append(genre)
                
                anime.genres = genres

            session.add(anime)
            await session.commit()
            print("Аниме и жанры успешно добавлены!")

        except Exception as exc:
            print(f"Ошибка: {exc}")
            await session.rollback()
            raise