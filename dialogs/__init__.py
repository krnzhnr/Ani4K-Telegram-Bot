from aiogram import Dispatcher

from . import bot_menu


def setup_dialogs_fun(dp: Dispatcher):
    """
    Функция для регистрации диалогов в диспетчере.
    Здесь добавляем все диалоги, которые будут использоваться в боте.
    """
    for dialog in [
        *bot_menu.bot_menu_dialogs(),  # Диалоги для меню бота
    ]:
        dp.include_router(dialog)  # Регистрируем диалог в диспетчере
