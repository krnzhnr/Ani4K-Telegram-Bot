# Импортируем классы для создания состояний FSM
from aiogram.fsm.state import StatesGroup, State


class BotMenu(StatesGroup):
    """
    Класс состояний для диалога бота.
    Содержит три состояния:
    - TITLES: Состояние выбора аниме.
    - EPISODES: Состояние выбора эпизодов.
    - EPISODE: Состояние конкретного эпизода.
    """
    TITLES = State()  # Состояние для выбора аниме
    EPISODES = State()  # Состояние для выбора эпизода
    EPISODE = State()  # Состояние для отображения информации об эпизоде
