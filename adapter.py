import json
import re
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, BotCommandScopeDefault
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from currency import get_exchange_rate
import game
import ai
import keyboards as kb
from states import BotStates
import random

router = Router()

with open("info.json", "r", encoding="utf-8") as f:
    info = json.load(f)

async def set_bot_commands(bot: Bot):
    hidden = ["goal", "story", "mentor", "progress", "hobbies", "works"]
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="games", description="Игры"),
        BotCommand(command="profile", description="Профиль"),
        BotCommand(command="about", description="Обо мне"),
        BotCommand(command="ai", description="ИИ"),
        BotCommand(command="support", description="Поддержка")
    ]
    for cmd in hidden:
        commands.append(BotCommand(command=cmd, description=cmd.capitalize()))
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())

@router.message(Command("start"))
@router.message(F.text == "⬅️ Назад")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await set_bot_commands(message.bot)
    await message.answer("📱 меню", reply_markup=kb.main_reply_menu())

@router.message(F.text == "🎮 Игры")
@router.message(Command("games"))
async def open_games(message: Message):
    await message.answer("🎮 Игры", reply_markup=kb.back_reply_menu())
    await message.answer("выбери игру:", reply_markup=kb.games_inline_menu())

@router.message(F.text == "👤 Профиль")
@router.message(Command("profile"))
async def open_profile(message: Message):
    user = game.profile(message.from_user.id)
    rank = game.get_rank(user['coin'])
    
    achievements_list = user.get("achievements", [])
    if not achievements_list:
        achievements_str = "Пока нет достижений"
    else:
        achievements_str = "\n".join([f"• {ach}" for ach in achievements_list])
        
    await message.answer(
        f"👤 ТВОЙ ПРОФИЛЬ:\n"
        f"⚡ Ранг: {rank}\n"
        f"───────────────────\n"
        f"💰 Баланс: {user['coin']} койнов\n"
        f"🎮 Сыграно игр: {user['played']}\n"
        f"🏆 Выиграно: {user['won']}\n"
        f"💀 Проиграно: {user['lost']}\n"
        f"───────────────────\n"
        f"🏅 Достижения:\n{achievements_str}",
        reply_markup=kb.back_reply_menu()
    )

RU_TITLES = {
    "about": "👤 Обо мне",
    "goal": "🎯 Моя цель",
    "story": "🚀 Как я пришёл в IT",
    "mentor": "🧠 Мой ментор",
    "progress": "📈 Точка А → Точка Б",
    "hobbies": "🎸 Хобби и интересы",
    "works": "💻 Мои лучшие работы",
    "dream": "✨Мечта"
}

@router.message(F.text == "👤 Обо мне")
@router.message(Command("about"))
async def open_about(message: Message):
    buttons = []
    
    for k in info:
        if k != "github" and k in RU_TITLES:
            buttons.append([InlineKeyboardButton(text=RU_TITLES[k], callback_data=f"info_{k}")])
            
    if "github" in info:
        buttons.append([InlineKeyboardButton(text="🐙 Мой GitHub", url=info["github"])])
        
    await message.answer("👤 раздел", reply_markup=kb.back_reply_menu())
    await message.answer("выбери пункт:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.message(F.text == "🤖 ИИ maboy")
@router.message(Command("ai"))
async def open_ai(message: Message, state: FSMContext):
    await state.set_state(BotStates.ai_mode)
    await message.answer(
        "🤖 го побазарим, пиши че хочешь\n\nчтобы закончить диалог — нажми кнопку ниже", 
        reply_markup=kb.ai_reply_menu()
    )

@router.message(BotStates.ai_mode)
async def ai_chat_handler(message: Message, state: FSMContext):
    if message.text.lower() in ["выход", "❌ выйти из ии"]:
        await state.clear()
        await message.answer("📱 меню", reply_markup=kb.main_reply_menu())
        return
        
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await message.answer(await ai.get_ai_response(message.text))

@router.message(F.text == "🆘 Поддержка")
@router.message(Command("support"))
async def open_support(message: Message):
    await message.answer("🆘 Поддержка: @godql")

@router.message(Command("goal", "story", "mentor", "progress", "hobbies", "works"))
async def handle_hidden_commands(message: Message):
    cmd_name = message.text.lower().replace("/", "")
    await message.answer(info.get(cmd_name, f"{cmd_name} не задано"), reply_markup=kb.back_reply_menu())

@router.callback_query(F.data.startswith("info_"))
async def callback_info_keys(call: CallbackQuery):
    await call.message.answer(info.get(call.data.replace("info_", ""), ""))
    await call.answer()

@router.callback_query(F.data == "dice")
async def callback_dice(call: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.dice_bet)
    await call.message.answer("💰 введи ставку")
    await call.answer()

@router.callback_query(F.data == "quiz")
async def callback_quiz(call: CallbackQuery, state: FSMContext):
    item = game.quiz_get()
    await state.set_state(BotStates.quiz_active)
    await state.update_data(current_quiz=item)
    await call.message.answer(item["q"])
    await call.answer()

@router.callback_query(F.data == "coin")
async def callback_coin(call: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.coin_bet)
    await call.message.answer("💰 Введи ставку")
    await call.answer()


@router.message(BotStates.coin_bet)
async def coin_bet_handler(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи число")
        return

    bet = int(message.text)

    if bet <= 0:
        await message.answer("❌ Ставка должна быть больше 0")
        return

    if bet > game.profile(message.from_user.id)["coin"]:
        await message.answer("❌ Недостаточно койнов")
        return

    await state.update_data(bet=bet)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🦅 Орёл", callback_data="coin_orel"),
                InlineKeyboardButton(text="🪙 Решка", callback_data="coin_reshka")
            ]
        ]
    )

    await message.answer("Выбери сторону:", reply_markup=markup)


@router.callback_query(F.data.startswith("coin_"))
async def coin_game_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    bet = data.get("bet", 0)

    choice = "орёл" if call.data == "coin_orel" else "решка"

    win, text = game.play_coin(
        call.from_user.id,
        bet,
        choice
    )

    await call.message.answer(text)
    await state.clear()
    await call.answer()

@router.message(BotStates.dice_bet)
async def dice_bet_handler(message: Message, state: FSMContext):
    if not re.match(r"^\d{1,9}$", message.text.strip()):
        await message.answer("❌ введи нормальное целое число")
        return
    bet = int(message.text)
    if bet <= 0:
        await message.answer("❌ ставка должна быть больше 0")
        return
    if bet > game.profile(message.from_user.id)["coin"]:
        await message.answer("❌ нет денег")
        return
    await state.update_data(bet=bet)
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📉 <3", callback_data="dice_low"),
        InlineKeyboardButton(text="⚖ =3", callback_data="dice_eq"),
        InlineKeyboardButton(text="📈 >3", callback_data="dice_high")
    ]])
    await message.answer("🎲 выбери:", reply_markup=markup)

@router.callback_query(F.data.startswith("dice_"))
async def dice_game_handler(call: CallbackQuery, state: FSMContext):
    choice = call.data.replace("dice_", "")
    data = await state.get_data()
    bet = data.get("bet", 0)
    result_text = game.play_dice(call.from_user.id, bet, choice)
    await call.message.answer(result_text)
    await state.clear()
    await call.answer()

@router.message(BotStates.quiz_active)
async def quiz_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    current_quiz = data.get("current_quiz")
    result_text = game.play_quiz(message.from_user.id, current_quiz, message.text)
    await message.answer(result_text)
    await state.clear()

@router.callback_query(F.data.startswith("cur_"))
async def currency_base_handler(call: CallbackQuery, state: FSMContext):
    print("CUR HANDLER WORKED")

    base_currency = call.data.replace("cur_", "")

    await state.update_data(base_currency=base_currency)
    await state.set_state(BotStates.currency_amount)

    await call.message.answer(
        f"💱 Первая валюта: {base_currency}\n\nВведите сумму:")

    await call.answer()

@router.callback_query(F.data == "exchange_usd")
async def currency_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.currency_base)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="USD", callback_data="cur_USD"),
                InlineKeyboardButton(text="EUR", callback_data="cur_EUR")
            ],
            [
                InlineKeyboardButton(text="RUB", callback_data="cur_RUB"),
                InlineKeyboardButton(text="KZT", callback_data="cur_KZT")
            ]
        ]
    )

    await call.message.answer(
        "💱 Выбери первую валюту",
        reply_markup=markup
    )
    await call.answer()

@router.callback_query(F.data.startswith("cur_"))
async def currency_base_handler(call: CallbackQuery, state: FSMContext):
    base_currency = call.data.replace("cur_", "")

    await state.update_data(base_currency=base_currency)
    await state.set_state(BotStates.currency_amount)

    await call.message.answer(
        f"💱 Первая валюта: {base_currency}\n\nВведите сумму:"
    )

    await call.answer()

@router.message(BotStates.currency_amount)
async def currency_amount_handler(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))

        await state.update_data(amount=amount)
        await state.set_state(BotStates.currency_target)

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="USD", callback_data="target_USD"),
                    InlineKeyboardButton(text="EUR", callback_data="target_EUR")
                ],
                [
                    InlineKeyboardButton(text="RUB", callback_data="target_RUB"),
                    InlineKeyboardButton(text="KZT", callback_data="target_KZT")
                ]
            ]
        )

        await message.answer(
            "💱 Выбери вторую валюту:",
            reply_markup=markup
        )

    except ValueError:
        await message.answer("❌ Введите число")

@router.callback_query(F.data.startswith("target_"))
async def currency_target_handler(call: CallbackQuery, state: FSMContext):
    target_currency = call.data.replace("target_", "")

    data = await state.get_data()

    base_currency = data.get("base_currency")
    amount = data.get("amount")

    try:
        rate = get_exchange_rate(base_currency, target_currency)

        result = amount * rate

        await call.message.answer(
            f"💱 Конвертация\n\n"
            f"{amount} {base_currency} = {result:.2f} {target_currency}"
        )

    except Exception as e:
        await call.message.answer(
            f"❌ Ошибка конвертации:\n{e}"
        )

    await state.clear()
    await call.answer()

@router.message(F.text)
async def unknown_message_handler(message: Message):
    await message.answer(
        "🤔 Я не понял эту команду.\n"
        "Пожалуйста, используйте кнопки меню ниже для навигации!",
        reply_markup=kb.main_reply_menu())