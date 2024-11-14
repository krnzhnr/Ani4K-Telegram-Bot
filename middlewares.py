from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import Message
from typing import Callable, Dict, Awaitable
from typing import Any

class PrivateChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Проверка, что сообщение пришло из личного чата или канала
        if isinstance(event, Message) and event.chat.type in ['group', 'supergroup']:
            # Если это группа или супергруппа, игнорируем сообщение
            return  # Сообщение не передается дальше
        
        # Если сообщение из личного чата или канала, передаем в следующий обработчик
        return await handler(event, data)
