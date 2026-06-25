import random
import json
import os

DATA_FILE = "players.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_scores, f, ensure_ascii=False, indent=4)

user_scores = load_data()

MULTIPLIER = 1.97
START_COINS = 1000

def get_profile(user_id):
    user_id = str(user_id)

    if user_id not in user_scores:
        user_scores[user_id] = {
            "coin": START_COINS,
            "played": 0,
            "won": 0,
            "lost": 0,
            "achievements": []
        }
    return user_scores[user_id]

def profile(user_id):
    return get_profile(user_id)

def get_rank(coins):
    """Считает статус программиста по его балансу для профиля"""
    if coins < 1200:
        return "👶 Стажёр (кодит за еду)"
    elif coins < 2500:
        return "💪 Крепкий Джун (пишет баги)"
    elif coins < 5000:
        return "🧠 Уверенный Мидл (дебажит прод)"
    else:
        return "👑 Тимлид-Сеньор (сидит на созвонах)"

def add_achievement(user_id, ach_text):
    """Безопасно добавляет ачивку в профиль"""
    p = get_profile(user_id)
    if "achievements" not in p:
        p["achievements"] = []
    if ach_text not in p["achievements"]:
        p["achievements"].append(ach_text)
        return True
    return False

def update_balance(user_id, amount, is_win=None):
    p = get_profile(user_id)

    p["coin"] += amount

    if is_win is not None:
        p["played"] += 1

        if is_win:
            p["won"] += 1

            if p["won"] >= 5:
                add_achievement(user_id, "🎰 Лудоман (5 побед)")
        else:
            p["lost"] += 1

            if p["lost"] >= 5:
                add_achievement(user_id, "📉 Сливной бачок (5 лузов)")

    save_data()
    return p["coin"]

def play_coin(user_id, bet, user_choice):
    p = get_profile(user_id)
    if p["coin"] < bet:
        return False, "❌ нет денег"
    winning_side = random.choice(["орёл", "решка"])
    if user_choice.strip().lower() == winning_side:
        win_amount = int(bet * MULTIPLIER) - bet 
        update_balance(user_id, win_amount, is_win=True)
        return True, f"🎰 Выпало: {winning_side}! Ты выиграл {int(bet * MULTIPLIER)} койнов!"
    else:
        update_balance(user_id, -bet, is_win=False)
        return False, f"📉 Выпало: {winning_side}. Ставка {bet} койнов улетела в зрительный зал."

def play_dice(user_id, bet, user_choice):
    roll = random.randint(1, 6)

    p = get_profile(user_id)
    if p["coin"] < bet:
        return "❌ нет денег"

    win = False

    if user_choice == "low" and roll < 3:
        win = True
    elif user_choice == "eq" and roll == 3:
        win = True
    elif user_choice == "high" and roll > 3:
        win = True

    if win:
        win_amount = int(bet * MULTIPLIER) - bet
        update_balance(user_id, win_amount, is_win=True)
        return f"🎲 Выпало: {roll}! Выиграл {int(bet * MULTIPLIER)} койнов!"
    else:
        update_balance(user_id, -bet, is_win=False)
        return f"🎲 Выпало: {roll}! Проиграл {bet} койнов."

def trigger_event(user_id):
    score = random.randint(-50, 100)
    if score >= 0:
        update_balance(user_id, score)
        return f"🍀 Повезло! Вы нашли заначку разработчика. (+{score} койнов)", score
    else:
        p = get_profile(user_id)
        if p["coin"] + score < 0:
            score = -p["coin"] 
        update_balance(user_id, score)
        add_achievement(user_id, "💥 Разрушитель Прода")
        return f"💥 Упс! Вы случайно сломали прод и заплатили штраф. ({score} койнов)", score

quiz = [
    {"q": "Столица Казахстана?", "a": ["астана"]},
    {"q": "Самая горячая планета?", "a": ["венера"]},
    {"q": "Сколько планет в Солнечной системе?", "a": ["8"]},
    {"q": "Какой язык является основным для нативной Android-разработки наряду с Kotlin?", "a": ["java"]},
    {"q": "Как называется тип данных, принимающий True или False?", "a": ["bool", "boolean", "булево", "булев"]},
    {"q": "Какое ключевое слово используется для создания функций в Python?", "a": ["def"]},
    {"q": "Как называется оператор остатка от деления в Python? (символ)", "a": ["%"]},
    {"q": "Какой встроенный метод измеряет длину строки или списка?", "a": ["len"]},
    {"q": "Как расшифровывается API?", "a": ["application programming interface"]},
    {"q": "Какая структура данных в Python хранит пары ключ-значение?", "a": ["dict", "словарь"]}
]

def quiz_get():
    return random.choice(quiz)

def play_quiz(user_id, current_quiz, user_answer):
    if user_answer.strip().lower() in current_quiz["a"]:
        update_balance(user_id, 100, is_win=True)
        add_achievement(user_id, "🧠 Эрудит (Квиз)")
        return "🏆 Правильно! +100"
    else:
        update_balance(user_id, 0, is_win=False)
        return "💀 Неверно! 0 койнов"

used_promocodes = {}

def activate_promocode(user_id, code):
    user_id = str(user_id)
    code = code.lower()

    if user_id not in used_promocodes:
        used_promocodes[user_id] = []

    if code in used_promocodes[user_id]:
        return False, "❌ Этот промокод уже использован"

    rewards = {
        "activcodes": 10000,
        "6days": 6000
    }

    if code not in rewards:
        return False, "❌ Неверный промокод"

    reward = rewards[code]

    update_balance(user_id, reward)

    used_promocodes[user_id].append(code)

    save_data()

    return True, f"🎁 Промокод активирован! +{reward} койнов"

save_data()