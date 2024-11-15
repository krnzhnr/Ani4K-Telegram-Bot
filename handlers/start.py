from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.menu_kb import menu_kb
from config_reader import config
from aiogram.utils.keyboard import ReplyKeyboardBuilder


router = Router()


@router.message(Command('admin'))
async def cmd_start(message: Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer(
            'Приветствую! Перед тобой меню.',
            reply_markup=menu_kb()
            # reply_markup=ReplyKeyboardRemove()
        )
    else:
        pass
