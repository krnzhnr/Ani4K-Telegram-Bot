# Импорты из сторонних библиотек
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery
from typing import Any

# Локальные импорты
from .states import BotMenu  # Импорт состояний для перехода между окнами
from .getters import get_episodes_data  # Функция для получения данных о эпизодах

# Функция обработчика выбора аниме
async def on_title_chosen(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    """
    Обрабатывает выбор аниме пользователем. Сохраняет выбранное аниме в контексте
    и инициирует переход к окну выбора эпизодов.
    """
    # Сохраняем ID выбранного аниме в контексте
    ctx = manager.current_context()
    ctx.dialog_data['anime_id'] = item_id

    # Переход к окну выбора эпизодов
    await manager.switch_to(BotMenu.EPISODES)


# Функция обработчика выбора эпизода
async def on_episode_chosen(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    """
    Обрабатывает выбор эпизода пользователем. Сохраняет ID выбранного эпизода в контексте
    и переходит к окну с выбранным эпизодом.
    """
    # Сохраняем выбранный episode_id в контексте
    manager.current_context().dialog_data['episode_id'] = item_id

    # Переход к окну с выбранным эпизодом
    await manager.switch_to(BotMenu.EPISODE)
