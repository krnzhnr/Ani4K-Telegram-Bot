import asyncio
from aiogram import Bot, Dispatcher
from handlers import start, create_post, create_notification, menu, auto_reposter
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_reader import config
from models.models import init_db


async def main():
    await init_db()
    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_routers(start.router, create_post.router, create_notification.router, menu.router, auto_reposter.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    print('Бот запущен!')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())