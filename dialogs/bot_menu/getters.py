# Импорты из сторонних библиотек
from sqlalchemy.future import select
from sqlalchemy import func
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram.enums import ContentType
from typing import Dict, List

# Импорт моделей и сессии для работы с базой данных
from models.models import Anime, Episode, Subscription, async_session
from utils.terminal import success, error, warning, info, debug


# --- Закомментированный код (оставляем на месте с пояснениями) ---
# async def get_anime_data(dialog_manager: DialogManager, **kwargs) -> Dict:
#     async with async_session() as session:
#         # Запрос на получение аниме с количеством всех эпизодов
#         result = await session.execute(
#             select(Anime.id, Anime.release_name, Anime.episodes_count)
#             .join(Episode, Episode.anime_id == Anime.id, isouter=True)
#             .group_by(Anime.id)
#         )
#
#         anime_list = []
#         for row in result.fetchall():
#             anime_id = row[0]
#             # Подсчитываем количество доступных эпизодов (например, просто количество эпизодов)
#             available_episodes = await session.execute(
#                 select(func.count(Episode.id)).filter(Episode.anime_id == anime_id)
#             )
#             available_episodes_count = available_episodes.scalar()
#
#             # Разделяем название, если есть символ "/"
#             release_name = row[1].split('/')[0]  # Получаем название до первого слэша
#
#             # Добавляем в список
#             anime_list.append({
#                 "id": row[0],
#                 "name": release_name,  # Название аниме без части после "/"
#                 "episodes_count": row[2],  # Общее количество эпизодов из Anime
#                 "available_episodes": available_episodes_count  # Доступные эпизоды
#             })
#
#     return {"anime_list": anime_list}
# --- Конец закомментированного кода ---


# Функция для получения данных по аниме
async def get_anime_data(dialog_manager: DialogManager, **kwargs) -> Dict:
    try:
        print(info("Запуск запроса к базе данных для получения данных по аниме."))

        async with async_session() as session:
            # Запрос на получение аниме с учетом даты последнего эпизода
            result = await session.execute(
                select(
                    Anime.id,
                    Anime.release_name,
                    Anime.episodes_count,
                    func.max(Episode.added_at)  # Дата последнего добавленного эпизода
                )
                .join(Episode, Episode.anime_id == Anime.id, isouter=True)
                .group_by(Anime.id)
                .order_by(func.max(Episode.added_at).desc())  # Сортировка по дате
            )

            # Получаем все строки результата
            result_list = result.fetchall()

            print(info(f"Найдено {len(result_list)} аниме в базе данных."))  # Принт с количеством найденных аниме

            anime_list = []
            for row in result_list:
                anime_id = row[0]
                release_name = row[1].split('/')[0].strip()  # Название до слэша
                episodes_count = row[2]
                last_episode_date = row[3]

                # print(debug(f"Обрабатывается аниме: {release_name} (ID: {anime_id})"))

                # Подсчитываем количество доступных эпизодов
                available_episodes = await session.execute(
                    select(func.count(Episode.id)).filter(Episode.anime_id == anime_id)
                )
                available_episodes_count = available_episodes.scalar()

                anime_list.append({
                    "id": anime_id,
                    "name": release_name,
                    "episodes_count": episodes_count,
                    "available_episodes": available_episodes_count,
                    "last_episode_date": last_episode_date
                })

            print(success(f"Получены данные по {len(anime_list)} аниме.\n**************************************************************************"))
            return {"anime_list": anime_list}

    except Exception as e:
        print(error(f"Произошла ошибка при выполнении запроса: {e}"))
        raise e


# Функция для получения данных об эпизодах аниме и статусе подписки
async def get_episodes_data(dialog_manager: DialogManager, **kwargs) -> Dict:
    anime_id = dialog_manager.current_context().dialog_data.get('anime_id')
    user_id = dialog_manager.event.from_user.id  # ID пользователя Telegram

    if not anime_id:
        print(warning("Не найден anime_id в контексте диалога. Возвращаем пустые данные."))
        return {
            'episode_list': [], 
            'poster': None, 
            'anime_name': '', 
            'anime_description': '', 
            'voice_type': '', 
            'voice_team': '',
            'is_subscribed': False,
            'subscribe_text': 'Подписаться'  # По умолчанию кнопка для подписки
        }

    print(info(f"Получение данных для аниме с ID: {anime_id}"))

    async with async_session() as session:
        try:
            # Проверяем, подписан ли пользователь на обновления аниме
            print(info(f"Проверка подписки пользователя с ID: {user_id} на аниме ID: {anime_id}"))
            subscription_result = await session.execute(
                select(Subscription.id)
                .filter(Subscription.user_id == user_id, Subscription.anime_id == anime_id)
            )
            is_subscribed = subscription_result.scalar() is not None
            subscribe_text = "🔕 Отписаться" if is_subscribed else "🔔 Подписаться"
            print(info(f"Статус подписки: {'Подписан' if is_subscribed else 'Не подписан'}"))

            # Извлекаем название, постер, описание, тип озвучки и команду озвучки
            print(info(f"Запрос к базе данных для аниме ID: {anime_id}."))
            anime_result = await session.execute(
                select(Anime.release_name, Anime.poster_id, Anime.description, Anime.dub, Anime.dub_team)
                .filter(Anime.id == anime_id)
            )
            anime_data = anime_result.fetchone()

            if anime_data:
                print(info(f"Данные по аниме получены: {anime_data[0]}"))
            else:
                print(warning("Данные по аниме не найдены в базе."))

            # Разделяем название по слешу, если он есть
            release_name = anime_data[0].split('/')[0].strip() if anime_data else ""
            poster_id = anime_data[1] if anime_data else None

            # Обрезаем описание до 750 символов и добавляем многоточие, если оно слишком длинное
            description = anime_data[2] if anime_data else "Описание отсутствует"
            if len(description) > 750:
                description = description[:750].rstrip() + "..."
                print(debug(f"Описание слишком длинное, обрезано до 750 символов"))

            # Определяем тип озвучки
            voice_type = "Дубляж" if anime_data[3] == 'dubbed' else "Закадровая озвучка"
            voice_team = anime_data[4] if anime_data[4] else "Неизвестная команда"

            print(info(f"Тип озвучки: {voice_type}, Команда озвучки: {voice_team}"))

            # Извлекаем список эпизодов
            print(info(f"Запрос на эпизоды для аниме ID: {anime_id}."))
            episode_result = await session.execute(
                select(Episode.id, Episode.episode_number)
                .filter(Episode.anime_id == anime_id)
                .order_by(Episode.episode_number)
            )
            episode_list = [{"id": row[0], "episode_number": row[1]} for row in episode_result.fetchall()]
            print(info(f"Найдено {len(episode_list)} эпизодов для аниме '{release_name}'."))

        except Exception as e:
            print(error(f"Произошла ошибка при получении данных об аниме: {e}"))
            raise e

    # Создаём MediaAttachment для постера
    poster = None
    if poster_id:
        print(info("Создание MediaAttachment для постера"))
        poster = MediaAttachment(
            type=ContentType.PHOTO,
            file_id=MediaId(poster_id)
        )

    print(success(f"Данные по аниме '{release_name}' успешно получены.\n**************************************************************************"))

    return {
        'episode_list': episode_list,
        'poster': poster,
        'anime_name': release_name,
        'anime_description': description,
        'voice_type': voice_type,
        'voice_team': voice_team,
        'is_subscribed': is_subscribed,
        'subscribe_text': subscribe_text  # Текст кнопки в зависимости от статуса подписки
    }


# Функция для получения данных о конкретном эпизоде
async def get_episode_data(dialog_manager: DialogManager, **kwargs):
    episode_id = dialog_manager.current_context().dialog_data.get("episode_id")
    
    if not episode_id:
        print(warning("Не найден episode_id в контексте диалога. Возвращаем пустые данные."))
        return {'video': None}
    
    print(info(f"Получение данных для эпизода с ID: {episode_id}"))

    async with async_session() as session:
        try:
            # Запрос к базе данных для получения данных о эпизоде
            print(info(f"Запрос к базе данных для эпизода с ID: {episode_id}."))
            result = await session.execute(
                select(Episode.media_id, Episode.episode_number, Anime.release_name)
                .join(Anime, Anime.id == Episode.anime_id)
                .filter(Episode.id == episode_id)
            )
            episode = result.fetchone()

            if episode:
                print(info(f"Данные по эпизоду получены: {episode.release_name}, Эпизод номер: {episode.episode_number}"))
                
                # Обрезаем название аниме до первого слэша
                release_name = episode.release_name.split('/')[0].strip()
                print(debug(f"Обрезанное название аниме: '{release_name}'"))

                # Создаем объект MediaAttachment для видео
                media = MediaAttachment(
                    type=ContentType.VIDEO,
                    file_id=MediaId(episode.media_id)
                )
                print(success(f"Успешно открыт эпизод: {episode.episode_number}\n**************************************************************************"))
                
                return {
                    'video': media,
                    'anime_name': release_name,  # Обрезанное название
                    'episode_number': episode.episode_number
                }
            else:
                print(warning(f"Эпизод с ID: {episode_id} не найден в базе данных."))

        except Exception as e:
            print(error(f"Произошла ошибка при получении данных о эпизоде: {e}"))
            raise e

    print(warning(f"Возвращаем пустое значение для эпизода с ID: {episode_id}."))
    return {'video': None}


async def get_subscription_data(dialog_manager, **kwargs):
    """Получение данных о подписке для настройки кнопки."""
    is_subscribed = dialog_manager.dialog_data.get('is_subscribed', False)  # Данные из контекста
    return {"subscribe_text": "Отписаться" if is_subscribed else "Подписаться"}