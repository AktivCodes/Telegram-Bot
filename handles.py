import asyncio
from aiogram import F
from aiogram.fsm.context import FSMContext
from states import BotStates
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from weather import get_weather
import game

router = Router()

from aiogram.types import Message, CallbackQuery

@router.callback_query(F.data == "weather")
async def weather_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.weather_city)

    await call.message.answer("🌤 Введите название города")

    await call.answer()


@router.message(BotStates.weather_city)
async def weather_handler(message: Message, state: FSMContext):
    city = message.text.strip()

    weather = get_weather(city)

    await message.answer(weather)

    await state.clear()

@router.message(Command("dice"))
async def dice_cmd(message: Message):
    
    dice_msg = await message.answer_dice(emoji="🎲")
    
    await asyncio.sleep(3.5)
    
    result = game.play_dice(message.from_user.id, bet=10, user_choice="high", roll=dice_msg.dice.value)
    
    await message.answer(result)

@router.message(Command("event"))
async def event_cmd(message: Message):
    text, score = game.trigger_event(message.from_user.id)
    p = game.profile(message.from_user.id)
    await message.answer(f"{text}\n⭐ очки: {p['coin']}")

@router.message(Command("daily"))
async def daily_cmd(message: Message):
    ok, amount = game.daily(message.from_user.id)
    if ok:
        await message.answer(f"🎁 +{amount} монет!")
    else:
        await message.answer("⏳ уже забрал сегодня")

@router.message(Command("profile"))
async def profile_cmd(message: Message):
    p = game.profile(message.from_user.id)
    await message.answer(f"👤 профиль\n⭐ очки: {p['coin']}")

@router.message(Command("promo"))
async def promo_cmd(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            "Использование:\n/promo ActivCodes"
        )
        return

    ok, text = game.activate_promocode(
        message.from_user.id,
        args[1]
    )

    await message.answer(text)
