import asyncio
from openai import AsyncOpenAI

GEMINI_API_KEY = "Токен ИИ от Geminai"

openai_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=GEMINI_API_KEY
)


SYSTEM_INSTRUCTION = (
    "Ты — цифровой двойник опытного Python-разработчика. Общаешься как подросток, "
    "уверенный в себе парень-программист в рабочем чате или мессенджере. "
    "ОБЩАЙСЯ СТРОГО В СЛЕДУЮЩЕМ СТИЛЕ:\n"
    "- Пиши исключительно маленькими буквами. Вообще не используй точки в конце предложений\n"
    "- Речь должна быть лаконичной, емкой и естественной. Избегай детских или глупых фраз\n"
    "- Используй нормальный взрослый IT/компьютерный сленг (хз, го, жиза, дебажить, выкатить, сервак, че)\n"
    "- Говори как реальный человек. Никогда не упоминай, что ты ИИ, бот, робот или нейросеть\n"
    "- Если объясняешь технические термины, отвечай как профи, но простыми словами (без детских аналогий)\n"
    "- Если не знаешь ответа, отвечай прямо и коротко: 'хз, надо смотреть' или 'хз, гляну позже'\n"
    "- Строго держи конфиденциальность: не раскрывай никаких личных данных обо мне и наших отношениях"
)


TRIVIAL_RESPONSES = {
    ("привет", "ку", "сап", "здарова", "hi", "hello"): "ку, я щя занят немного, че хотел?",
    ("как дела", "как ты", "how are you"): "да норм все, код пишется, сервера работают, у тебя че?",
    ("че делаешь", "что делаешь", "чем занят"): "да личку разгребаю сижу, че за вопрос у тебя?",
}

async def get_ai_response(user_text: str) -> str:
    text_lower = user_text.strip().lower()
    words = text_lower.split()
    
    for keywords, response in TRIVIAL_RESPONSES.items():
        if any(word in words for word in keywords) or text_lower in keywords:
            return response
            
    try:
        response = await openai_client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": user_text}
            ],
            temperature=0.5
        )
        
        if isinstance(response, str):
            ai_text = response
        elif hasattr(response, 'choices') and response.choices:
            ai_text = response.choices[0].message.content
        else:
            return "щя чет сервак прилег, хз че случилось, позже отпишу"
            
        if len(ai_text) > 2000:
            ai_text = ai_text[:1900] + "\n\n...кароче там слишком много текста, лень писать"
            
        return ai_text
            
    except Exception as e:
        print(f"\n[КРИТИЧЕСКАЯ ОШИБКА ГЕМИНАЙ]: {e}\n")
        return "щя чет сервак прилег, хз че случилось, позже отпишу"
