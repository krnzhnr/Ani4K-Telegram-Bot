from aiogram import Dispatcher

from . import bot_menu


def setup_dialogs_fun(dp: Dispatcher):
    for dialog in [
        *bot_menu.bot_menu_dialogs(),
    ]:
        dp.include_router(dialog)  # register a dialog