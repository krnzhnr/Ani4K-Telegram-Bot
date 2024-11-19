from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, Back
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.media import DynamicMedia

from .getters import get_anime_data, get_episodes_data, get_episode_data
from .selected import on_title_chosen, on_episode_chosen
from .states import BotMenu


# Максимальное количество кнопок на странице
PAGE_SIZE = 7


def titles_window():
    """
    Окно выбора аниме. Отображает список аниме с доступными эпизодами.
    При клике на аниме переходим к выбору эпизодов.
    """
    return Window(
        Const("Выберите аниме:"),  # Текст в верхней части окна
        ScrollingGroup(  # Группа с прокручиваемыми кнопками
            Select(
                text=Format("[{item[available_episodes]}/{item[episodes_count]}] {item[name]}"),
                id="anime_button",  # ID для кнопки
                item_id_getter=lambda item: item["id"],  # Получение ID из данных
                items="anime_list",  # Список аниме, получаемый из getter
                on_click=on_title_chosen  # Обработчик события нажатия
            ),
            id="titles",  # ID для группы
            width=1,  # Ширина группы (по сути, это кол-во кнопок в строке)
            height=PAGE_SIZE,  # Высота группы (количество видимых кнопок)
        ),
        Cancel(Const("Закрыть")),  # Кнопка для закрытия
        state=BotMenu.TITLES,  # Состояние окна в диалоге
        getter=get_anime_data  # Получатель данных для списка аниме
    )


def episodes_window():
    """
    Окно выбора эпизодов для выбранного аниме.
    Отображает информацию о выбранном аниме и список эпизодов.
    """
    return Window(
        DynamicMedia("poster"),  # Показываем постер аниме
        Format(
            "<b><u>{anime_name}</u></b>\n\n"
            "<blockquote expandable>{anime_description}</blockquote>\n\n"
            "{voice_type}, {voice_team}\n\n"
            "Эпизоды:"
        ),  # Форматированный текст с информацией о аниме
        ScrollingGroup(  # Группа с прокручиваемыми кнопками
            Select(
                text=Format("{item[episode_number]} эпизод"),  # Текст кнопки с номером эпизода
                id="episode_button",  # ID кнопки
                item_id_getter=lambda item: item["id"],  # Получение ID эпизода
                items="episode_list",  # Список эпизодов, получаемый из getter
                on_click=on_episode_chosen  # Обработчик нажатия
            ),
            id="episodes",  # ID для группы
            width=3,  # Ширина группы
            height=PAGE_SIZE,  # Высота группы
        ),
        Back(Const('<<< Назад к тайтлам')),  # Кнопка для возврата на экран с аниме
        state=BotMenu.EPISODES,  # Состояние для выбора эпизодов
        getter=get_episodes_data  # Получатель данных для списка эпизодов
    )


def episode_window():
    """
    Окно с информацией об эпизоде. Показывает видео эпизода и основные детали.
    """
    return Window(
        Format("<b><u>{anime_name}</u></b>\n\n{episode_number} эпизод"),  # Текст с названием и номером эпизода
        DynamicMedia("video"),  # Встраиваем медиа (видеофайл)
        Back(Const("<<< Назад к эпизодам")),  # Кнопка для возврата к списку эпизодов
        state=BotMenu.EPISODE,  # Состояние для конкретного эпизода
        getter=get_episode_data  # Получатель данных для эпизода
    )
