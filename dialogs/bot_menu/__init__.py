from aiogram_dialog import Dialog

from . import windows


def bot_menu_dialogs():
    return [
        Dialog(
            windows.titles_window(),
            windows.episodes_window(),
            windows.episode_window()
        )
    ]