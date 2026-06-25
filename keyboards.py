from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_reply_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Игры"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="👤 Обо мне"), KeyboardButton(text="🤖 ИИ maboy")],
            [KeyboardButton(text="🆘 Поддержка")]
        ],
        resize_keyboard=True
    )

def back_reply_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )

def games_inline_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🪙 Орёл и Решка", callback_data="coin"),
                InlineKeyboardButton(text="🎲 Кубик", callback_data="dice")
            ],
                        [
                InlineKeyboardButton(text="🌤 Погода", callback_data="weather"),
                InlineKeyboardButton(text="💵 Курс денег", callback_data="exchange_usd")
            ],
            [
                InlineKeyboardButton(text="❓ Квиз", callback_data="quiz")
            ]

        ]
    )

def ai_reply_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Выйти из ИИ")]],
        resize_keyboard=True
    )
