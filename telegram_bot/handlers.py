from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, Document
from aiogram.fsm.context import FSMContext
from .states import Registration
from .database import get_user, set_user, update_language, update_level
from .keyboards import language_keyboard, level_keyboard, main_menu_keyboard
from book_processor import process_book

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user(user_id):
        await message.answer("Вы уже зарегистрированы!", reply_markup=main_menu_keyboard())
    else:
        await message.answer("Выберите язык обучения:", reply_markup=language_keyboard())
        await state.set_state(Registration.choosing_language)

@router.callback_query(F.data.startswith("lang_"))
async def process_language(callback: CallbackQuery, state: FSMContext):
    language = callback.data.split("_")[1]
    await state.update_data(language=language)
    await callback.message.edit_text("Выберите уровень владения языком:", reply_markup=level_keyboard())
    await state.set_state(Registration.choosing_level)

@router.callback_query(F.data.startswith("level_"))
async def process_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    data = await state.get_data()
    language = data.get("language")
    user_id = callback.from_user.id
    set_user(user_id, language, level)
    await callback.message.edit_text("Вы зарегистрированы!", reply_markup=main_menu_keyboard())
    await state.clear()

@router.callback_query(F.data == "change_lang")
async def change_language(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите новый язык:", reply_markup=language_keyboard())
    await state.set_state(Registration.choosing_language)

@router.callback_query(F.data == "change_level")
async def change_level(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите новый уровень:", reply_markup=level_keyboard())
    await state.set_state(Registration.choosing_level)

@router.callback_query(F.data == "upload_book")
async def ask_book(callback: CallbackQuery):
    await callback.message.answer("Пожалуйста, отправьте файл книги (EPUB, PDF и т.п.).")

@router.message(F.document)
async def handle_file_upload(message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if not user:
        await message.answer("Вы не зарегистрированы. Введите /start")
        return
    language, level = user[1], user[2]
    file = message.document
    file_path = f"user_uploads/{file.file_name}"
    await message.bot.download(file, destination=file_path)
    result = process_book(file_path, language, level)
    await message.answer(result)
