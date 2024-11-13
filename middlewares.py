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
        # Проверка, что сообщение пришло из личного чата
        if isinstance(event, Message) and event.chat.type != 'private':
            # Если не личный чат, просто игнорируем обработку
            pass
            # return await event.answer("❌ Этот бот работает только в личных сообщениях.")
        # Если все ок, передаем в следующий обработчик
        return await handler(event, data)
