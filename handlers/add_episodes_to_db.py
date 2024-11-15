from aiogram.types import Message
from aiogram import Router, F, Bot
from database import check_anime_exists, add_episode

import re


router = Router()


@router.message(F.video & F.caption)
async def handle_video_message(message: Message, bot: Bot):
    # Извлекаем ID видео и подпись
    video_id = message.video.file_id
    caption = message.caption

    if not caption:
        await message.answer("Отправьте видео с подписью.")
        return

    # Извлекаем информацию из подписи
    episode_info = extract_episode_info(caption)
    episode_info['media_id'] = video_id
    print(f"Extracted info: {episode_info}")

    anime_name = episode_info.get('anime_name')
    if not anime_name:
        await message.answer("Не удалось извлечь название аниме из подписи.")
        return

    # Проверка наличия аниме в базе
    anime = await check_anime_exists(anime_name)
    if anime:
        result_message = await add_episode(anime, episode_info)  # получаем сообщение из add_episode
        await message.answer(result_message)  # отправляем его в чат
    else:
        await message.answer(f"Аниме '{anime_name}' не найдено в базе. Сначала добавьте его.")


def extract_episode_info(caption: str):
    # Шаблон для извлечения названия аниме до первого номера эпизода
    anime_name_pattern = r"^\[?\d*\]?\s*(.*?)\s*(?=\d+\s*эпизод)"  # Теперь \[?\d*\]? — необязательные скобки
    # Шаблон для номера эпизода
    episode_pattern = r"(\d+)\s*эпизод"
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




