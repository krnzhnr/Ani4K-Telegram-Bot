import asyncio
import logging

from aiogram import Bot, Router, F, types
from aiogram.types import Message
from utils.terminal import success, error, warning, info, debug


# Настройка логирования
# logging.basicConfig(level=logging.INFO)

# Константы для идентификаторов каналов и чатов
CHANNEL_ID = '-1001995806263'  # ID канала (Основной: -1001995806263, тестовый: -1002303815016)
CHAT_ID = '-1002104882531'     # ID чата

# Инициализация роутера для обработки сообщений
router = Router()


async def sleep():
    """
    Функция, выполняющая паузу на 60 секунд.
    """
    print(info('Сон 60 секунд...'))
    await asyncio.sleep(60)
    print(info("Сон выполнен"))
    return True


@router.channel_post(F.text)
async def forward_message(
    channel_post: types.Message,
    bot: Bot
):
    """
    Обработчик сообщений из канала. Если сообщение поступает из указанного канала (CHANNEL_ID),
    пересылает его в заданный чат (CHAT_ID) после 60-секундной задержки.
    
    Args:
        channel_post (types.Message): Сообщение из канала.
        bot (Bot): Экземпляр бота.
    """
    # Проверяем, из нужного ли канала пришло сообщение
    if channel_post.chat.id == CHANNEL_ID:
        print(info(f"Обнаружен пост: {channel_post.text or channel_post.caption}"))

        # Выполняем задержку перед пересылкой
        if await sleep() is True:
            print(info(f"Пересылаю пост: {channel_post.text or channel_post.caption}"))
            await bot.forward_message(CHAT_ID, CHANNEL_ID, channel_post.message_id)
    else:
        print(info('Обнаружен пост в тестовом канале. Пропускаю...'))
        pass
