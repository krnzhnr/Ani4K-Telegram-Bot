from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message
from typing import Callable, Dict, Awaitable, Any
from colorama import init, Fore
from utils.terminal import success, error, warning, info, debug


init(autoreset=True)

CHAT_ID = -1002104882531
CHAT_ID = int(CHAT_ID)

# Функция проверки принадлежности пользователя к группе
async def is_user_in_group(user_id: int, bot: Bot, group_id: str) -> bool:
    try:
        chat_member = await bot.get_chat_member(group_id, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(error(f"[Middleware] Ошибка проверки членства в группе: {e}"))
        return False


class PrivateChatMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, group_id: str):
        self.bot = bot
        self.group_id = group_id
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Если сообщение из группы (не супергруппа), пропускаем без обработки
        if isinstance(event, Message) and event.chat.type == 'group':
            print(warning("[Middleware] Сообщение из обычной группы. Пропускаю..."))
            return  # Сообщение не передается дальше

        # Если сообщение из супергруппы
        if isinstance(event, Message) and event.chat.type == 'supergroup':
            print(info("[Middleware] Сообщение из супергруппы. Передаю дальше..."))
            # Проверяем, совпадает ли chat_id с ожидаемым
            if event.chat.id != int(self.group_id):
                print(warning(f"[Middleware] Сообщение из супергруппы '{event.chat.title or 'Без названия'}' ({event.chat.id}), но ожидается 'Ani4K HUB'. Пропускаю..."))
                return  # Пропускаем сообщение, если оно не из нужной супергруппы
            
            # Проверка, является ли это сообщение из топика
            if not event.is_topic_message:
                print(warning("[Middleware] Сообщение не из топика. Пропускаю..."))
                return  # Пропускаем, если сообщение не из топика

            # Проверка, пришло ли сообщение от имени самой группы (для анонимного администратора)
            if event.sender_chat and event.sender_chat.id == CHAT_ID:
                print(info("[Middleware] Сообщение от имени самой группы (анонимный администратор). Передаю дальше..."))
                return await handler(event, data)  # Передаем дальше для анонимного администратора

            # Если сообщение пришло от админа или создателя супергруппы (бот или создатель)
            if event.from_user.id == CHAT_ID or event.sender_chat and event.sender_chat.id == CHAT_ID:
                print(info("[Middleware] Сообщение от бота или создателя. Передаю дальше..."))
                return await handler(event, data)  # Пропускаем обработку для бота или создателя

            # Если сообщение не от создателя и не от бота, игнорируем
            print(warning(f"[Middleware] Сообщение от пользователя {event.from_user.full_name}. Пропускаю..."))
            return  # Сообщение не передается дальше

        # Если сообщение из личного чата, проверяем, состоит ли пользователь в группе
        if isinstance(event, Message):
            user_id = event.from_user.id
            user_fullname = event.from_user.full_name
            if not await is_user_in_group(user_id, self.bot, self.group_id):
                print(warning(f'[Middleware] {user_fullname} пытался взаимодействовать с ботом. Пропускаю...'))
                await event.answer("Вы должны быть членом нашей группы, чтобы использовать бота.")
                return  # Сообщение не передается дальше, если пользователь не в группе
        
        # Пропускаем сообщение дальше, если оно прошло все проверки
        return await handler(event, data)
