from aiogram_dialog import Window, Data, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Back, Next, Row, SwitchTo, Cancel, ScrollingGroup, Button, Select
from aiogram_dialog.widgets.text import Format, Const
from .getters import get_buttons_data
from .states import BotMenu
from typing import List


# Максимальное количество кнопок на странице
PAGE_SIZE = 10


# Асинхронное создание кнопок тайтлов
async def btns_creator(anime_list: List[str]):
    buttons = [Button(Const(anime), id=anime) for anime in anime_list]
    return buttons


# Создаём кнопки динамически на основе данных из getter
def create_buttons(data):
    return [Button(Const(item["text"]), id=item["id"]) for item in data["buttons"]]


# Создание Select для отображения кнопок на основе данных
anime_selector = Select(
    text=Format("{item[name]}"),  # Текст кнопки будет названием аниме
    id="anime_button",
    item_id_getter=lambda item: item["id"],  # Используем ID из базы данных
    items="anime_list",  # Используем данные из getter
)


# Создание окна
def titles_window():
    return Window(
        Const("Выберите аниме:"),
        ScrollingGroup(
            anime_selector,
            id='titles',
            width=1,
            height=PAGE_SIZE
        ),
        Cancel(Const('Закрыть')),
        state=BotMenu.TITLES,
        getter=get_buttons_data  # Асинхронный getter для подгрузки данных
    )



