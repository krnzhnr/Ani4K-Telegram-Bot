from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from dialogs.bot_menu.states import BotMenu


router = Router()


@router.message(Command('menu'))
async def get_menu(message: Message, dialog_manager: DialogManager):
    # Мы начинаем диалог с первого состояния
    await dialog_manager.start(BotMenu.TITLES, mode=StartMode.RESET_STACK)