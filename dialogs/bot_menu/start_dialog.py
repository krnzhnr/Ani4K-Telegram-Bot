# Импорты из сторонних библиотек
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

# Локальные импорты
from dialogs.bot_menu.states import BotMenu  # Состояния диалога
from utils.terminal import success, error, warning, info, debug


# Инициализация роутера и ID чата
router = Router()
chat_id = '-1002104882531'


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
    Обрабатывает команду /start. Проверяет, состоит ли пользователь в группе.
    Если да, начинает диалог с первым состоянием, если нет - отправляет сообщение о том,
    что пользователь не может получить доступ.
    """
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    # Логирование: выводим информацию о пользователе
    print(info(f"Получена команда /start от пользователя {full_name} (ID: {user_id}, Username: {username})"))

    # Закомментированная проверка наличия пользователя в группе
    # if await is_user_in_group(user_id, bot):
    #     print(f'{full_name} (ID: {user_id}, Username: {username}) открыл меню.')
    #     await dialog_manager.start(BotMenu.TITLES, mode=StartMode.RESET_STACK)
    # else:
    #     print(f'{full_name} (ID: {user_id}, Username: {username}) не состоит в группе, доступ к меню закрыт.')
    #     await message.answer(
    #         'Я не могу ответить на запрос, так как вы не состоите в нашей группе.'
    #     )

    # Прямой запуск диалога без проверки
    print(info(f'{full_name} (ID: {user_id}, Username: {username}) открыл меню.'))
    await dialog_manager.start(BotMenu.TITLES, mode=StartMode.RESET_STACK)
    print(info(f"Диалог с {full_name} (ID: {user_id}) был запущен с начальным состоянием меню."))