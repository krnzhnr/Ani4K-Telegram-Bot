from aiogram import Router, F, types, Bot
from aiogram.types import Message, ReplyKeyboardRemove, PhotoSize
from keyboards.menu_kb import create_post_start_kb, creation_cancel_kb
from keyboards.create_post_kb import choice_dub_kb, create_post_finish_kb, create_post_channel_selection_kb, create_post_channel_test, CreatePostCallbackActions, ChoiceDubCallbackActions
from keyboards.menu_kb import menu_kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, StateFilter
from aiogram.methods import SendMessage, send_photo
import re

router = Router()

post = {}

ADMIN_ID = 491203291
CHAT_ID = '-1002104882531'  # ID чата


class PostCreation(StatesGroup):
    channel_selection = State()
    add_poster = State()
    add_name = State()
    add_description = State()
    add_episodes = State()
    add_dub = State()
    add_genres_and_topics = State()
    # add_hashtags = State()




@router.callback_query(CreatePostCallbackActions.filter(F.action == 'create_announcement'))
async def create_post_channel_selection(
    callback: types.CallbackQuery,
    callback_data: CreatePostCallbackActions,
    state: FSMContext
):
    await callback.message.edit_text('Выбери канал для поста.', reply_markup=create_post_channel_selection_kb())
    await state.set_state(PostCreation.channel_selection)
    await callback.answer()




@router.callback_query(CreatePostCallbackActions.filter(F.action == 'main_channel'))
async def main_channel_selected(
    callback: types.CallbackQuery,
    callback_data: CreatePostCallbackActions,
    state: FSMContext
):
    if callback.message.chat.id == ADMIN_ID:
        post.update({'channel_id': '-1001995806263'})
        print(f'{callback.message.chat.full_name} выбрал канал ОСНОВНОЙ, ID = {post['channel_id']}')
        await callback.message.edit_text(
            f'Выбран канал: <strong>Основной</strong>.\n\nПришли мне постер.',
            reply_markup=creation_cancel_kb()
        )
        await state.set_state(PostCreation.add_poster)
        await callback.answer()
    else:
        await callback.message.edit_text(
            f'Тебе, {callback.message.chat.full_name}, там делать нечего, так что давай ты выберешь <strong>тестовый</strong> и мы не будем с тобой ругаться.',
            reply_markup=create_post_channel_test()
        )
        print(f'{callback.message.chat.full_name} пытался запостить в основу.')
        await callback.answer()




@router.callback_query(CreatePostCallbackActions.filter(F.action == 'test_channel'))
async def test_channel_selected(
    callback: types.CallbackQuery,
    callback_data: CreatePostCallbackActions,
    state: FSMContext
):
    post.update({'channel_id': '-1002303815016'})
    print(f'{callback.message.chat.full_name} выбрал канал ТЕСТОВЫЙ, ID = {post['channel_id']}')
    await callback.message.edit_text(
        f'Выбран канал: <strong>Тестовый</strong>.\n\nПришли мне постер.',
        reply_markup=creation_cancel_kb()
    )
    await state.set_state(PostCreation.add_poster)
    await callback.answer()




# @router.callback_query(CreatePostCallbackActions.filter(F.action == 'start'))
# async def create_post_start(
#     callback: types.CallbackQuery,
#     callback_data: CreatePostCallbackActions,
#     state: FSMContext
# ):
#     await callback.message.edit_text('Пришли мне постер.', reply_markup=creation_cancel_kb())
#     await state.set_state(PostCreation.add_poster)
#     await callback.answer()




# ПОЛУЧЕНИЕ ПОСТЕРА

@router.message(
    PostCreation.add_poster,
    F.photo[-1].as_('poster_img')
)
async def add_poster(message: Message, state: FSMContext, poster_img: PhotoSize, bot: Bot):
    post.update({'poster_id': poster_img.file_id})
    print(f'ID постера: {post['poster_id']}')
    await message.answer(
        text='Постер добавлен, дальше пришли полное название с Шикимори.',
        reply_markup=creation_cancel_kb()
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )
    await state.set_state(PostCreation.add_name)




# ПОЛУЧЕНИЕ НАЗВАНИЯ

@router.message(
    PostCreation.add_name,
    F.text
)
async def add_name(message: Message, state: FSMContext, bot: Bot):
    post.update({'release_name': message.text})
    print(f'Название: {post['release_name']}')
    await message.answer(
        text='Название добавлено, теперь пришли описание. Оно должно быть не длиннее 750 символов.',
        reply_markup=creation_cancel_kb()
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )    
    await state.set_state(PostCreation.add_description)




# ПОЛУЧЕНИЕ ОПИСАНИЯ

@router.message(
    PostCreation.add_description,
    F.text
)
async def add_descriprion(message: Message, state: FSMContext, bot: Bot):
    if len(message.text) < 750:
        post.update({'description': message.text})
        print(f'Описание: {post['description']}')
        await message.answer(
            text='Описание добавлено, теперь пришли количество эпизодов в формате "[Количество] эпизодов(-да)".',
            reply_markup=creation_cancel_kb()
        )
        await bot.delete_messages(
            message.chat.id,
            [message.message_id, message.message_id - 1]
        )
        await state.set_state(PostCreation.add_episodes)
    else:
        await message.answer(
            text=f'Текст описания слишком длинный и составляет {len(message.text)} символов, а надо не более 750, так что переписывай и присылай новое!',
            reply_markup=creation_cancel_kb()
        )
        await bot.delete_messages(
            message.chat.id,
            [message.message_id, message.message_id - 1]
        )




# ПОЛУЧЕНИЕ КОЛИЧЕСТВА ЭПИЗОДОВ

@router.message(
    PostCreation.add_episodes,
    F.text
)
async def add_episodes(message: Message, state: FSMContext, bot: Bot):
    post.update({'episodes': message.text})
    print(f'Количество эпизодов: {post['episodes']}')
    # await message.answer(str(post))
    await message.answer(
        text='Количество эпизодов добавлено, выбери тип озвучки:',
        reply_markup=choice_dub_kb()
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )




# ОБРАБОТКА НАЖАТИЯ КНОПКИ "ДУБЛИРОВАННЫЙ"
    
@router.callback_query(ChoiceDubCallbackActions.filter(F.dub == 'dubbed'))
async def dub_callback(
    callback: types.CallbackQuery,
    callback_data: ChoiceDubCallbackActions,
    state: FSMContext
):
    post.update({'dub': 'dubbed'})
    print(f'Тип озвучки: {post['dub']}')
    dub_type = post['dub']
    await callback.message.edit_text(
        f'Выбранный тип озвучки: <strong>Дубляж</strong>\n\nПришли название команды.',
        reply_markup=creation_cancel_kb()
    )
    await state.set_state(PostCreation.add_dub)
    await callback.answer(
        text=dub_type,
        show_alert=False
    )




# ОБРАБОТКА НАЖАТИЯ КНОПКИ "ЗАКАДРОВАЯ"

@router.callback_query(ChoiceDubCallbackActions.filter(F.dub == 'voiceover'))
async def voiceover_callback(
    callback: types.CallbackQuery,
    callback_data: ChoiceDubCallbackActions,
    state: FSMContext
):
    post.update({'dub': 'voiceover'})
    print(f'Тип озвучки: {post['dub']}')
    dub_type = post['dub']
    await callback.message.edit_text(
        f'Выбранный тип озвучки: <strong>Закадровая озвучка</strong>\n\nПришли название команды.',
        reply_markup=creation_cancel_kb()
    )
    await state.set_state(PostCreation.add_dub)
    await callback.answer(
        text=dub_type,
        show_alert=False
    )




# ВВОД НАЗВАНИЯ КОМАНДЫ ОЗВУЧКИ

@router.message(
    PostCreation.add_dub,
    F.text
)
async def add_dub(message: Message, state: FSMContext, bot: Bot):
    post.update({'dub_team': message.text})
    print(f'Команда озвучки: {post['dub_team']}')
    # await message.answer(str(post))
    await message.answer(
        text='Тип озвучки и команда добавлены, теперь пришли жанры и темы с Шикимори через пробел.',
        reply_markup=creation_cancel_kb()
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )
    await state.set_state(PostCreation.add_genres_and_topics)




# ВВОД ЖАНРОВ И ТЕМ + ЗАВЕРШЕНИЕ РАБОТЫ КОНЕЧНОГО АВТОМАТА

@router.message(
    PostCreation.add_genres_and_topics,
    F.text
)
async def add_genres_and_topics(message: Message, state: FSMContext, bot: Bot):
    genres_and_topics_list = message.text.split()
    topics_list = ''
    for topic in genres_and_topics_list:
        updated_topic = '#' + topic + ' '
        topics_list = topics_list + updated_topic
    post.update({'genres_and_topics': topics_list.title()})
    print(f'Жанры и темы: {post['genres_and_topics']}')
    await message.answer(
        text=f'Жанры и темы добавлены.\n\nВот итоговый вид поста:'
    )
    await bot.delete_messages(
        message.chat.id,
        [message.message_id, message.message_id - 1]
    )
    create_final_hashtags()
    await state.clear()
    try:
        await message.answer_photo(
            photo=post['poster_id'],
            caption=post_assembly(),
            reply_markup=create_post_finish_kb()
        )
        print(f'\n{message.from_user.full_name} собрал пост:\n\n{post}')
    except Exception as exc:
        await message.answer(str(exc))




# СБОРКА ХЭШТЕГОВ

def create_final_hashtags():
    name_hashtag = ''
    dub_team_hashtag = ''

    release_name = post['release_name']
    release_name = release_name.split('/')[0]
    release_name = re.sub(r'[^\w\s]', '', release_name)
    release_name = release_name.replace(' ', '_')
    release_name = release_name.strip('_')
    name_hashtag = f'#{release_name}'

    dub_team = post['dub_team']
    dub_team = re.sub(r'[^\w\s/-]', '', dub_team)
    dub_team = re.sub(r'[\s/-]+', '_', dub_team)
    dub_team_hashtag = f'#{dub_team}'

    final_hashtags = f'{name_hashtag} {dub_team_hashtag}'
    post.update({'hashtags': final_hashtags})
    print(post['hashtags'])




# СБОРКА ПОСТА

def post_assembly():
    if post['dub'] == 'dubbed':
        dub_type = 'Дубляж,'
    else:
        dub_type = 'Закадровая озвучка,'

    ready_post = f'<b><u>{post['release_name']}</u></b>\n\n<i><blockquote expandable>{post['description']}</blockquote></i>\n\n{post['episodes']}\n\n{dub_type} {post["dub_team"]}\n\n{post['genres_and_topics']}\n\n{post['hashtags']}'
    return ready_post




# ОБРАБОТКА ПУБЛИКАЦИИ

@router.callback_query(CreatePostCallbackActions.filter(F.action == 'publish'))
async def post_publish(
    callback: types.CallbackQuery,
    callback_data: CreatePostCallbackActions,
    bot: Bot
):
    try:
        sent_message = await bot.send_photo(
            chat_id=post['channel_id'],
            photo=post['poster_id'],
            caption=post_assembly()
        )
        await callback.message.answer(
            text='Пост опубликован, можно создавать новый.',
            reply_markup=create_post_start_kb()
        )
        await bot.delete_messages(
            callback.message.chat.id,
            [callback.message.message_id, callback.message.message_id - 1]
        )
        await bot.forward_message(
            chat_id=CHAT_ID,
            from_chat_id=post['channel_id'],
            message_id=sent_message.message_id
        )
        post.clear()
        await callback.answer()
    except Exception as exc:
        print(exc)
        await callback.message.edit_text(
            text=f'Что-то пошло не так, вот причина:\n\n{exc}'
        )
        await callback.answer()




# ОБРАБОТКА ОТМЕНЫ ГОТОВОГО ПОСТА

@router.callback_query(CreatePostCallbackActions.filter(F.action == 'finish_cancel'))
async def post_cancel(
    callback: types.CallbackQuery,
    callback_data: CreatePostCallbackActions,
    state: FSMContext,
    bot: Bot
):
    await state.clear()
    post.clear()
    await callback.message.answer(
        text='Пост удален, можно создавать новый.',
        reply_markup=menu_kb()
    )
    await bot.delete_messages(
        callback.message.chat.id,
        [callback.message.message_id, callback.message.message_id - 1]
    )
    await callback.answer()




# ОБРАБОТКА ОТМЕНЫ В ПРОЦЕССЕ СОЗДАНИЯ

@router.callback_query(CreatePostCallbackActions.filter(F.action == 'creation_cancel'))
async def creation_cancel(
    callback: types.CallbackQuery,
    callback_data: CreatePostCallbackActions,
    state: FSMContext,
    bot: Bot
):
    await state.clear()
    post.clear()
    await callback.message.answer(
        text='Создание поста отменено, перед тобой меню.',
        reply_markup=menu_kb()
    )
    await bot.delete_messages(
        callback.message.chat.id,
        [callback.message.message_id, callback.message.message_id - 1]
    )
    await callback.answer()


