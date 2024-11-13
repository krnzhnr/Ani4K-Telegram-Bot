from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from database import get_anime_list
from typing import Dict


# Асинхронный getter для загрузки данных в диалог
async def get_buttons_data(dialog_manager: DialogManager, **kwargs) -> Dict:
    anime_list = await get_anime_list()
    return {"anime_list": anime_list}