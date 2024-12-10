# Импорты из сторонних библиотек
from datetime import datetime
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from datetime import datetime, timezone, timedelta

# Локальные импорты
from dialogs.bot_menu.states import BotMenu  # Состояния диалога
from utils.terminal import success, error, warning, info, debug
from database import upsert_user


# Инициализация роутера и ID чата
router = Router()
chat_id = '-1002104882531'

# Определим часовой пояс для Беларуси
belarus_timezone = timezone(timedelta(hours=3))



# Функция для проверки, состоит ли пользователь в группе
# async def is_user_in_group(user_id, bot: Bot):
#     """
#     Проверяет, является ли пользователь участником группы.
#     Возвращает True, если пользователь - участник, администратор или создатель,
#     иначе возвращает False.
#     """
#     try:
#         chat = await bot.get_chat(chat_id=chat_id)
#         chat_member = await bot.get_chat_member(chat_id, user_id)
#         return chat_member.status in ['member', 'administrator', 'creator']
#     except Exception as e:
#         print(f"Error checking group membership: {e}")
#         return False


# Обработчик команды /start
@router.message(Command('start'))
async def get_menu(message: Message, dialog_manager: DialogManager, bot: Bot):
    """
    Обрабатывает команду /start. Сохраняет или обновляет данные пользователя
    в базе данных и запускает главное меню.
    """
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""
    full_name = message.from_user.full_name
    username = message.from_user.username or ""

    # Текущая дата взаимодействия
    interaction_date = datetime.now(belarus_timezone)

    # Сохраняем или обновляем данные о пользователе в базе данных
    await upsert_user(user_id, first_name, last_name, full_name, username, interaction_date)

    # Запускаем меню
    print(info(f'{full_name} (ID: {user_id}, Username: {username}) открыл меню.'))
    await dialog_manager.start(BotMenu.TITLES, mode=StartMode.RESET_STACK)
    print(info(f"Диалог с {full_name} (ID: {user_id}) был запущен с начальным состоянием меню."))