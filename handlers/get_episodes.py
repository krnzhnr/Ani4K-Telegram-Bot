from aiogram import types, Router
from aiogram.filters import Command
from database import get_episodes_for_anime, get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

# ============ НЕ ИСПОЛЬЗУЕТСЯ ============

# Обработчик команды /episodes 
@router.message(Command('episodes'))
async def episodes_command(message: types.Message):
    # Извлекаем аргумент из текста сообщения
    if message.text.startswith("/episodes"):
        release_name = message.text[len("/episodes"):].strip()  # Обрезаем команду и пробел

        if not release_name:
            await message.reply("Пожалуйста, укажите название аниме. Например: /episodes Дороро")
            return

        # Получаем эпизоды для указанного аниме
        episodes = await get_episodes_for_anime(release_name)

        if isinstance(episodes, str):  # Если это строка, значит произошла ошибка или аниме не найдено
            await message.reply(episodes)
        else:
            # Отправляем каждую серию по отдельности
            for episode_number, media_id in episodes:
                await message.answer_video(
                    video=media_id,
                    caption=f'Серия: {episode_number}'
                )