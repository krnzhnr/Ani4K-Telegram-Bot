from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery
from .states import BotMenu
from .getters import get_episodes_data
from typing import Any

# async def on_anime_selected(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
#     # Обновляем данные о выбранном аниме
#     ctx = manager.current_context()
#     ctx.dialog_data.update(anime_id=item_id)  # Сохраняем id аниме в диалоговых данных

#     # Переходим к окну с эпизодами
#     await manager.switch_to(BotMenu.EPISODES)


# @router.callback_query(F.data)
# async def on_episode_selected(c: CallbackQuery, manager: DialogManager, data: dict):
#     anime_id = manager.current_context().dialog_data["anime_id"]  # Получаем id аниме
#     episode_number = data["episode_number"]  # Получаем номер эпизода
#     # Дальше обработка выбранного эпизода


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
