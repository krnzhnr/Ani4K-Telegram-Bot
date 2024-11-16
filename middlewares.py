from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message
from typing import Callable, Dict, Awaitable, Any


# Функция проверки принадлежности пользователя к группе
async def is_user_in_group(user_id: int, bot: Bot, group_id: str) -> bool:
    try:
        chat_member = await bot.get_chat_member(group_id, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking group membership: {e}")
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
        # Если сообщение пришло из группы или супергруппы, сразу возвращаем
        if isinstance(event, Message) and event.chat.type in ['group', 'supergroup']:
            print('Обнаружено сообщение из группы. Пропускаю...')
            return  # Сообщение не передается дальше
        
        # Если сообщение из личного чата, проверяем, состоит ли пользователь в группе
        if isinstance(event, Message):
            user_id = event.from_user.id
            user_fullname = event.from_user.full_name
            if not await is_user_in_group(user_id, self.bot, self.group_id):
                print(f'{user_fullname} пытался взаимодействовать с ботом. Пропускаю...')
                await event.answer("Вы должны быть членом нашей группы, чтобы использовать бота.")
                return  # Сообщение не передается дальше, если пользователь не в группе
        
        return await handler(event, data)

# class PrivateChatMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any]
#     ) -> Any:
#         # Проверка, что сообщение пришло из личного чата или канала
#         if isinstance(event, Message) and event.chat.type in ['group', 'supergroup']:
#             # Если это группа или супергруппа, игнорируем сообщение
#             return  # Сообщение не передается дальше
        
#         # Если сообщение из личного чата или канала, передаем в следующий обработчик
#         return await handler(event, data)
