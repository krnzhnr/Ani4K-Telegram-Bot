from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Anime, Genre, Episode, User, Subscription, async_session
from utils.terminal import success, error, warning, info, debug
from sqlalchemy.orm import selectinload
from aiogram import Bot
from typing import List, Dict
import re
from datetime import datetime, timezone, timedelta

belarus_timezone = timezone(timedelta(hours=3))


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
                # print(warning(f"Аниме с названием '{data['release_name']}' уже существует."))
                return existing_anime  # Возвращаем уже существующее аниме

            # # Извлекаем количество эпизодов
            # episodes_number = re.search(r'\d+', data['episodes'])
            # episodes = int(episodes_number.group()) if episodes_number else 0
            
            # Проверка, если 'episodes' уже целое число
            if isinstance(data['episodes'], int):
                episodes = data['episodes']
            else:
                # Если это строка, извлекаем число
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
            # print(success(f"Аниме '{anime.release_name}' успешно добавлено!"))
            # return anime  # Возвращаем добавленное аниме
            return True

        except Exception as exc:
            print(error(exc))
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
            print(success(f"{len(episode_data_list)} эпизодов успешно добавлено к аниме '{anime.release_name}'!"))

        except Exception as exc:
            print(error(exc))
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
            print(warning(f"Эпизод {episode_info['episode_number']} для аниме '{anime.release_name}' уже существует в базе."))
            return f"❗️Эпизод {episode_info['episode_number']} для аниме '{anime.release_name}' уже существует в базе.", anime.release_name

        # Если эпизод не найден, добавляем новый
        new_episode = Episode(
            media_id=episode_info['media_id'],
            episode_number=episode_info['episode_number'],
            anime_id=anime.id
        )
        session.add(new_episode)
        await session.commit()

        # Успешное добавление
        print(success(f"Эпизод {episode_info['episode_number']} для аниме '{anime.release_name}' успешно добавлен."))
        return f"✅Эпизод {episode_info['episode_number']} для аниме '{anime.release_name}' успешно добавлен.", anime.release_name


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


async def upsert_user(user_id: int, first_name: str, last_name: str, full_name: str, username: str, interaction_date: datetime):
    """
    Добавляет нового пользователя или обновляет дату последнего взаимодействия
    для существующего пользователя.

    :param user_id: ID пользователя
    :param first_name: Имя пользователя
    :param second_name: Фамилия пользователя
    :param full_name: Полное имя пользователя
    :param username: Username пользователя
    :param interaction_date: Дата взаимодействия
    """
    async with async_session() as session:
        async with session.begin():
            # Ищем пользователя в базе данных
            user = await session.get(User, user_id)
            
            if user:  # Если пользователь уже существует
                user.last_interaction_date = interaction_date  # Обновляем дату последнего взаимодействия
                print(info(f"Обновлена дата последнего взаимодействия для пользователя {full_name} (ID: {user_id})."))
            else:  # Если пользователь новый
                user = User(
                    id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    username=username,
                    first_interaction_date=interaction_date,  # Устанавливаем дату первого взаимодействия
                    last_interaction_date=interaction_date   # Устанавливаем дату последнего взаимодействия
                )
                session.add(user)
                print(success(f"Добавлен новый пользователь: {full_name} (ID: {user_id})."))

        await session.commit()


async def add_subscription_to_db(user_id: int, anime_id: int):
    """
    Функция для добавления подписки в базу данных.
    Проверяет, есть ли уже подписка на это аниме у пользователя.
    Если подписки нет, создает новую.
    """
    async with async_session() as session:
        async with session.begin():
            # Проверка, есть ли у пользователя подписка на это аниме
            result = await session.execute(select(Subscription).filter_by(user_id=user_id, anime_id=anime_id))
            existing_subscription = result.scalars().first()  # Получаем первый результат

            if existing_subscription:
                return False  # Если подписка уже есть, возвращаем False

            # Создаем новую подписку
            new_subscription = Subscription(
                user_id=user_id,
                anime_id=anime_id,
                subscribed_at=datetime.now(belarus_timezone),  # Устанавливаем время подписки
            )
            
            session.add(new_subscription)
            
            # Обновляем время последнего обновления подписки для пользователя в таблице User
            user_stmt = select(User).filter_by(id=user_id)
            user_result = await session.execute(user_stmt)
            user = user_result.scalars().first()

            if user:
                user.subscriptions_last_updated = datetime.now(belarus_timezone)  # Обновляем время

            await session.commit()  # Сохраняем новую подписку в таблице Subscription

            return True  # Возвращаем True, если подписка была успешно добавлена


async def check_subscription_in_db(user_id, anime_id):
    """Проверяет, есть ли подписка в базе данных."""
    async with async_session() as session:
        async with session.begin():
            stmt = select(Subscription).filter_by(user_id=user_id, anime_id=anime_id)
            result = await session.execute(stmt)
            return result.scalars().first() is not None


async def remove_subscription_from_db(user_id, anime_id):
    """Удаляет подписку из базы данных и возвращает True, если подписка была удалена."""
    async with async_session() as session:
        async with session.begin():
            # Удаляем подписку из таблицы Subscription
            stmt = delete(Subscription).filter_by(user_id=user_id, anime_id=anime_id)
            result = await session.execute(stmt)

            # Проверяем, были ли затронуты строки (то есть подписка была удалена)
            if result.rowcount > 0:
                # Если подписка была удалена, обновляем поле subscriptions_last_updated в таблице User
                user_stmt = select(User).filter_by(id=user_id)
                user_result = await session.execute(user_stmt)
                user = user_result.scalars().first()

                if user:
                    user.subscriptions_last_updated = datetime.now(belarus_timezone)  # Обновляем время
                    await session.commit()  # Сохраняем изменения в таблице User

                return True
            return False  # Если не было удалено ни одной строки, возвращаем False


async def notify_subscribed_users(anime_id: int, episode_number: int, anime_name: str, bot: Bot):
    """
    Уведомление пользователей, подписанных на указанное аниме, о новом эпизоде.
    """
    async with async_session() as session:
        # Получаем список пользователей, подписанных на это аниме
        result = await session.execute(
            select(User).join(Subscription).filter(Subscription.anime_id == anime_id)
        )
        users = result.scalars().all()

        # Если подписчиков нет
        if not users:
            print(warning(f"Нет подписчиков на аниме '{anime_name}'"))
            return

        anime_name = anime_name.split('/')[0].strip()

        # Отправляем уведомления каждому подписчику
        for user in users:
            try:
                # Отправляем сообщение каждому пользователю
                await bot.send_message(
                    user.id,
                    f'🎬 Новый эпизод аниме <b><i>{anime_name}</i></b>! Эпизод <b>{episode_number}</b> теперь доступен.'
                )
                print(success(f"Уведомление отправлено пользователю {user.full_name} ({user.id}) о новом эпизоде аниме '{anime_name}'"))
            except Exception as e:
                # Обрабатываем ошибки, если не удалось отправить сообщение пользователю
                print(error(f"Не удалось отправить уведомление пользователю {user.id}: {e}"))
