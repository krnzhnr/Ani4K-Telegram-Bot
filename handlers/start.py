from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.menu_kb import create_post_start_kb, create_type_select_kb, start_kb
from aiogram.utils.keyboard import ReplyKeyboardBuilder


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        'Приветствую! Нажми на кнопку внизу чтобы открыть меню.',
        reply_markup=start_kb()
        # reply_markup=ReplyKeyboardRemove()
    )
