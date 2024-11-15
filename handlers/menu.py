from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.menu_kb import create_post_start_kb, create_type_select_kb, start_kb, menu_kb, CreatePostCallbackActions
from aiogram.utils.keyboard import ReplyKeyboardBuilder


router = Router()


@router.message(F.text.lower() == 'меню')
async def get_menu(message: Message, bot: Bot):
    await message.answer(
        'Перед тобой меню бота, для выбора действия нажми на соответствующую кнопку.',
        reply_markup=menu_kb()
    )
    try:
        await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )
    except:
        await bot.delete_message(message.chat.id, message.message_id)


@router.callback_query(CreatePostCallbackActions.filter(F.action == 'create'))
async def lets_create(
    callback: types.CallbackQuery,
    callback_data: CreatePostCallbackActions
):
    await callback.message.edit_text(
        text='Отлично! Выбери, что будешь создавать.',
        reply_markup=create_type_select_kb()
    )
    await callback.answer()