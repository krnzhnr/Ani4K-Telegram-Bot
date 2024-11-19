from aiogram_dialog import Dialog
from . import windows  # Импортируем окна из локального модуля

def bot_menu_dialogs():
    """
    Возвращает список диалогов для меню бота.
    """
    return [
        Dialog(
            windows.titles_window(),   # Окно с заголовками
            windows.episodes_window(), # Окно с эпизодами
            windows.episode_window()   # Окно для конкретного эпизода
        )
    ]
