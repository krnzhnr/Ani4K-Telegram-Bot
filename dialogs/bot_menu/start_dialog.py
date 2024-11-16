from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from dialogs.bot_menu.states import BotMenu
from config_reader import config


router = Router()
chat_id = '-1002104882531'


async def is_user_in_group(user_id, bot: Bot):
    try:
        chat = await bot.get_chat(chat_id=chat_id)
        # print(chat)
        chat_member = await bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking group membership: {e}")
        return False


@router.message(Command('start'))
async def get_menu(message: Message, dialog_manager: DialogManager, bot: Bot):
    # Мы начинаем диалог с первого состояния
    user_id = message.from_user.id
    if await is_user_in_group(user_id, bot):
        print(f'{message.from_user.full_name} открыл меню.')
        await dialog_manager.start(BotMenu.TITLES, mode=StartMode.RESET_STACK)
    else:
        await message.answer(
            'Я не могу ответить на запрос, так как вы не состоите в нашей группе.'
        )