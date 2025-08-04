from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English", callback_data="lang_en")],
        [InlineKeyboardButton(text="Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton(text="Español", callback_data="lang_es")],
    ])

def level_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Beginner (A1–A2)", callback_data="level_a")],
        [InlineKeyboardButton(text="Intermediate (B1–B2)", callback_data="level_b")],
        [InlineKeyboardButton(text="Advanced (C1–C2)", callback_data="level_c")],
    ])

def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Загрузить книгу", callback_data="upload_book")],
        [InlineKeyboardButton(text="🌐 Изменить язык", callback_data="change_lang")],
        [InlineKeyboardButton(text="📈 Изменить уровень", callback_data="change_level")],
    ])
