from aiogram import Bot, Router, F, types
from aiogram.types import Message
import asyncio
import logging

# logging.basicConfig(level=logging.INFO)

CHANNEL_ID = '-1001995806263'  # ID канала -1001995806263 тестовый - -1002303815016
CHAT_ID = '-1002104882531'  # ID чата

router = Router()


async def sleep():
    print('Сон 60 секунд...')
    await asyncio.sleep(60)
    print("Сон выполнен")
    return True


@router.channel_post(F.text)  # Обработчик для всех сообщений
async def forward_message(
    channel_post: types.Message,
    bot: Bot
):
    if channel_post.chat.id == CHANNEL_ID:
        print(f"Обнаружен пост: {channel_post.text or channel_post.caption}")
        if await sleep() is True:
            print(f"Пересылаю пост: {channel_post.text or channel_post.caption}")
            await bot.forward_message(CHAT_ID, CHANNEL_ID, channel_post.message_id)
    else:
        print('Обнаружен пост в тестовом канале. Пропускаю...')
        pass

