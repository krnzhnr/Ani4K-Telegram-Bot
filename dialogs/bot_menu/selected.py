# Импорты из сторонних библиотек
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery
from typing import Any

# Локальные импорты
from .states import BotMenu  # Импорт состояний для перехода между окнами
from .getters import get_episodes_data  # Функция для получения данных о эпизодах
from utils.terminal import success, error, warning, info, debug
from database import add_subscription_to_db, check_subscription_in_db, remove_subscription_from_db


# Функция обработчика выбора аниме
async def on_title_chosen(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    """
    Обрабатывает выбор аниме пользователем. Сохраняет выбранное аниме в контексте
    и инициирует переход к окну выбора эпизодов, обновляя данные о подписке.
    """
    print(info(f"Выбор аниме: {item_id}"))  # Принт о выбранном аниме

    # Сохраняем ID выбранного аниме в контексте
    ctx = manager.current_context()
    ctx.dialog_data['anime_id'] = item_id

    # Проверяем подписку пользователя
    user_id = c.from_user.id
    is_subscribed = await check_subscription_in_db(user_id, item_id)
    ctx.dialog_data['is_subscribed'] = is_subscribed  # Сохраняем статус подписки

    print(info(f"Сохранено аниме с ID: {item_id} в контексте."))  # Подтверждение сохранения
    print(info(f"Подписка на аниме: {'Есть' if is_subscribed else 'Нет'}"))  # Информация о подписке

    # Переход к окну выбора эпизодов
    await manager.switch_to(BotMenu.EPISODES)
    print(info(f"Переход к окну выбора эпизодов."))  # Принт о переходе к следующему окну


# Функция обработчика выбора эпизода
async def on_episode_chosen(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    """
    Обрабатывает выбор эпизода пользователем. Сохраняет ID выбранного эпизода в контексте
    и переходит к окну с выбранным эпизодом.
    """
    print(info(f"Выбор эпизода: {item_id}"))  # Принт о выбранном эпизоде

    # Сохраняем выбранный episode_id в контексте
    manager.current_context().dialog_data['episode_id'] = item_id

    print(info(f"Сохранен эпизод с ID: {item_id} в контексте."))  # Подтверждение сохранения

    # Переход к окну с выбранным эпизодом
    await manager.switch_to(BotMenu.EPISODE)
    print(info(f"Переход к окну выбранного эпизода."))  # Принт о переходе к следующему окну


async def on_title_subscribed(c: CallbackQuery, widget: Any, manager: DialogManager):
    """
    Обрабатывает нажатие на кнопку "Подписка на обновления".
    Добавляет подписку для пользователя на выбранное аниме, если её нет.
    """
    user_id = c.from_user.id  # Получаем ID пользователя
    ctx = manager.current_context()  # Получаем текущий контекст диалога
    anime_id = ctx.dialog_data.get("anime_id")  # Получаем ID аниме из контекста
    is_subscribed = ctx.dialog_data.get("is_subscribed")  # Статус подписки
    subscribe_text = ctx.dialog_data.get("subscribe_text")  # Текст кнопки

    if not anime_id:
        await c.message.answer("Не удалось найти выбранное аниме.")
        return

    try:
        if is_subscribed:
            # Если пользователь подписан, то отписываем
            success = await remove_subscription_from_db(user_id, anime_id)
            if success:
                subscribe_text = "Подписаться"  # Меняем текст кнопки на "Подписаться"
                await c.answer(f"Вы отписались от обновлений (ID: {anime_id}).")
            else:
                await c.answer(f"Ошибка при отписке от обновлений (ID: {anime_id}).")
        else:
            # Если пользователь не подписан, то подписываем
            success = await add_subscription_to_db(user_id, anime_id)
            if success:
                subscribe_text = "Отписаться"  # Меняем текст кнопки на "Отписаться"
                await c.answer(f"Вы подписались на обновления (ID: {anime_id}).")
            else:
                await c.answer(f"Ошибка при подписке на обновления (ID: {anime_id}).")

        # Обновляем статус подписки и текст кнопки в контексте
        ctx.dialog_data["is_subscribed"] = not is_subscribed
        ctx.dialog_data["subscribe_text"] = subscribe_text

        # Обновляем текст кнопки в интерфейсе
        await manager.update(data=ctx.dialog_data)

    except Exception as e:
        print(error(f"Произошла ошибка при обработке подписки: {e}"))
        # await c.answer(e)