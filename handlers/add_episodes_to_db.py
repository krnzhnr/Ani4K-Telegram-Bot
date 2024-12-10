import re
from aiogram import Router, F, Bot
from aiogram.types import Message
from database import check_anime_exists, add_episode, notify_subscribed_users  # Локальные импорты для работы с базой данных
from config_reader import config
from utils.terminal import success, error, warning, info, debug


router = Router()


@router.message(F.video & F.caption)
async def handle_video_message(message: Message, bot: Bot):
    """
    Обработка видеосообщений с подписью.
    Извлекаем данные из подписи, проверяем наличие аниме в базе и добавляем эпизод.
    """
    if message.from_user.id == config.ADMIN_ID or message.is_topic_message:  # Проверка соответствия ID пользователя и ID админа
        print(info("Обнаружен новый эпизод."))
        # Извлекаем ID видео и подпись
        video_id = message.video.file_id
        caption = message.caption

        if not caption:
            await bot.send_message(config.ADMIN_ID, "Отправьте видео с подписью.")  # Отправляем в личку админу
            print(error("У эпизода отсутствует описание."))
            return

        # Извлекаем информацию из подписи
        episode_info = extract_episode_info(caption)
        episode_info['media_id'] = video_id
        print(debug(f"Извлеченная информация: {episode_info}"))

        anime_name = episode_info.get('anime_name')
        if not anime_name:
            await bot.send_message(config.ADMIN_ID, "❗️ Не удалось извлечь название аниме из подписи.")
            print(error("Не удалось извлечь название аниме из подписи."))
            return

        # Проверка наличия аниме в базе
        anime = await check_anime_exists(anime_name)
        if anime:
            result_message, anime_name = await add_episode(anime, episode_info)  # Получаем сообщение и название аниме
            await bot.send_message(config.ADMIN_ID, result_message)  # Отправляем сообщение админу
            # Уведомляем подписанных пользователей
            await notify_subscribed_users(anime.id, episode_info['episode_number'], anime_name, bot)
        else:
            await bot.send_message(config.ADMIN_ID, f"❗️ Аниме '{anime_name}' не найдено в базе. Сначала добавьте его.")
            print(warning(f"Аниме '{anime_name}' не найдено в базе."))


def extract_episode_info(caption: str):
    """
    Извлекает информацию о названии аниме, номере эпизода, типе озвучки и команде озвучки из подписи.
    """
    # Шаблон для извлечения названия аниме до первого номера эпизода
    anime_name_pattern = r"^\[?\d*\]?\s*(.*?)\s*(?=\d+\s*эпизод)"  # Теперь \[?\d*\]? — необязательные скобки
    # Шаблон для номера эпизода
    episode_pattern = r"(\d+)\s*(серия|эпизод)"
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
