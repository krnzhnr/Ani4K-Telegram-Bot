from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def text_message(message: Message):
    await message.answer('Это текстовое сообщение!')

@router.message(F.sticker)
async def sticker_message(message: Message):
    await message.answer('Это стикер!')

@router.message(F.animation)
async def gif_message(message: Message):
    await message.answer('Это гифка!')

@router.message(F.emoji)
async def emoji_message(message: Message):
    await message.answer('Это эмодзи!')