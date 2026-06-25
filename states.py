from aiogram.fsm.state import StatesGroup, State

class BotStates(StatesGroup):
    dice_bet = State()
    quiz_active = State()
    ai_mode = State()

    coin_bet = State()
    coin_choice = State()

    currency_base = State()
    currency_amount = State()
    currency_target = State()

    weather_city = State()