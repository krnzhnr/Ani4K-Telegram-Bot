from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery
from .states import BotMenu
from .getters import get_episodes_data
from typing import Any


async def on_title_chosen(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    # Сохраняем ID выбранного аниме в контексте
    ctx = manager.current_context()
    ctx.dialog_data['anime_id'] = item_id

    # Переход к окну выбора эпизодов
    await manager.switch_to(BotMenu.EPISODES)


async def on_episode_chosen(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    # Сохраняем выбранный episode_id в контексте
    manager.current_context().dialog_data['episode_id'] = item_id
    await manager.switch_to(BotMenu.EPISODE)  # Переходим к окну с выбранным эпизодом
