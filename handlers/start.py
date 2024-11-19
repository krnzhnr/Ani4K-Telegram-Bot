from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.menu_kb import menu_kb
from config_reader import config


router = Router()


# ============ ОТКРЫТИЕ АДМИНСКОГО МЕНЮ СОЗДАНИЯ ПОСТОВ ============

@router.message(Command('admin'))
async def cmd_start(message: Message):
    if message.from_user.id == config.ADMIN_ID:  # Проверка соответствия ID пользователя и ID админа
        await message.answer(
            'Приветствую! Перед тобой меню.',
            reply_markup=menu_kb()
            # reply_markup=ReplyKeyboardRemove()  # Используется чтобы убрать клавиатуру с кнопками у пользователей
        )
    else:
        pass
