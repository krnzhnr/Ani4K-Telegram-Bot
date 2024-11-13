from aiogram_dialog import Dialog

from . import windows


def bot_menu_dialogs():
    return [
        Dialog(
            windows.titles_window()
            # on_process_result=windows.on_process_result,
        )
        # Dialog(
        #     windows.buy_product_window(),
        #     windows.confirm_buy_window(),
        # ),
    ]