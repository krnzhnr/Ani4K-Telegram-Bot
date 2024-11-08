from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Anime, engine, async_session

async def add_anime_from_dict(data: dict):
    async with async_session() as session:  # создаем сессию в асинхронном контексте
        try:
            print(f"Session type: {type(session)}")

            # Пытаемся найти уже существующее аниме по названию
            result = await session.execute(
                select(Anime).where(Anime.release_name == data['release_name'])
            )
            existing_anime = result.scalars().first()
            if existing_anime:
                print("Аниме с таким названием уже существует.")
                return

            # Создание нового объекта Anime
            anime = Anime(
                poster_id=data['poster_id'],
                release_name=data['release_name'],
                description=data['description'],
                episodes=data['episodes'],
                dub=data['dub'],
                dub_team=data['dub_team'],
                hashtags=data['hashtags']
            )
            session.add(anime)

            # Коммит изменений в базе данных
            await session.commit()
            print("Аниме успешно добавлено!")

        except Exception as exc:
            print(f"Ошибка: {exc}")
            await session.rollback()
            raise
