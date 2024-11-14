from aiogram_dialog import Window, Data, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Back, Next, Row, SwitchTo, Cancel, ScrollingGroup, Button, Select
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram.enums import ContentType
from .getters import get_anime_data, get_episodes_data, get_episode_data
from .states import BotMenu
from .selected import on_title_chosen, on_episode_chosen
from typing import List


# Максимальное количество кнопок на странице
PAGE_SIZE = 12


# # Создание Select для отображения кнопок на основе данных
# anime_selector = Select(
#     text=Format("{item[name]}"),  # Текст кнопки будет названием аниме
#     id="anime_button",
#     item_id_getter=lambda item: item["id"],  # Используем ID из базы данных
#     items="anime_list",  # Используем данные из getter
# )


# # Создание окна
# def titles_window():
#     return Window(
#         Const("Выберите аниме:"),
#         ScrollingGroup(
#              # Создаем Select, используя уже обработанный список с названиями
#             Select(
#                 text=Format("{item[name]}"),  # Отображаем уже очищенное имя
#                 id="anime_button",
#                 item_id_getter=lambda item: item["id"],  # ID из базы данных
#                 items="anime_list",  # Данные будут переданы через геттер
#             ),
#             id="titles",
#             width=1,
#             height=PAGE_SIZE,
#         ),
#         Cancel(Const("Закрыть")),
#         state=BotMenu.TITLES,
#         getter=get_anime_data  # Асинхронный геттер для подгрузки данных
#     )

# Создание окна
def titles_window():
    return Window(
        Const("Выберите аниме:"),
        ScrollingGroup(
            Select(
                text = Format("[{item[available_episodes]}/{item[episodes_count]}] {item[name]}"),
                id="anime_button",
                item_id_getter=lambda item: item["id"],
                items="anime_list",
                on_click=on_title_chosen  # Переход при выборе
            ),
            id="titles",
            width=1,
            height=PAGE_SIZE,
        ),
        Cancel(Const("Закрыть")),
        state=BotMenu.TITLES,
        getter=get_anime_data
    )




def episodes_window():
    return Window(
        DynamicMedia("poster"),  # Отображаем постер тайтла
        Format(
            "<b><u>{anime_name}</u></b>\n\n"
            "<blockquote expandable>{anime_description}</blockquote>\n\n"
            "{voice_type}, {voice_team}\n\n"
            "Эпизоды:"
        ),  # Динамическое отображение информации о тайтле
        ScrollingGroup(
            Select(
                text=Format("{item[episode_number]} эпизод"),
                id="episode_button",
                item_id_getter=lambda item: item["id"],
                items="episode_list",
                on_click=on_episode_chosen
            ),
            id="episodes",
            width=1,
            height=PAGE_SIZE,
        ),
        Back(Const('<<< Назад к тайтлам')),
        state=BotMenu.EPISODES,
        getter=get_episodes_data
    )




def episode_window():
    return Window(
        Format("<b><u>{anime_name}</u></b>\n\n{episode_number} эпизод"),
        DynamicMedia("video"),
        Back(Const("<<< Назад к эпизодам")),
        state=BotMenu.EPISODE,
        getter=get_episode_data
    )