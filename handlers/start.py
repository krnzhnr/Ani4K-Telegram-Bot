from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.create_post_kb import create_post_start_kb
from aiogram.utils.keyboard import ReplyKeyboardBuilder




router = Router()



@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        'Приветствую! Пора создать новый пост.',
        reply_markup=create_post_start_kb()
        # reply_markup=ReplyKeyboardRemove()
    )
