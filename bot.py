import asyncio
from aiogram import Bot, Dispatcher
from handlers import add_title_to_db, start, create_post, create_notification, menu, auto_reposter, get_episodes, add_episodes_to_db
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_reader import config
from models.models import init_db
from aiogram_dialog import setup_dialogs
from dialogs import setup_dialogs_fun
from dialogs.bot_menu import start_dialog
from middlewares import PrivateChatMiddleware


async def main():
    await init_db()
    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Регистрируем middleware
    group_id = '-1002104882531'
    
    dp.message.middleware(PrivateChatMiddleware(bot, group_id))

    dp.include_routers(start.router, create_post.router, create_notification.router, menu.router, auto_reposter.router, get_episodes.router, add_episodes_to_db.router, add_title_to_db.router, start_dialog.router)
    
    # Настройка aiogram_dialog
    setup_dialogs_fun(dp)
    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    print('Бот запущен!')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())