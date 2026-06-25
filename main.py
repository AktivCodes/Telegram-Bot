import asyncio
import sys
import logging
from aiogram import Bot, Dispatcher
from handles import router
from adapter import router as adapter_router

DEBUG_MODE = "--debug" in sys.argv or "-debug" in sys.argv

if DEBUG_MODE:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.ERROR)

async def main():
    bot_token = None
    
    for arg in sys.argv:
        if arg.startswith("--token=") or arg.startswith("-token="):
            parts = arg.split("=")
            if len(parts) > 1:
                bot_token = parts[1]
            break
            
    if not bot_token and len(sys.argv) > 1:
        pos_arg = sys.argv[1]
        if not pos_arg.startswith("-"):
            bot_token = pos_arg

    if not bot_token:
        print("\n❌ Ошибка: не указан токен бота!")
        print("Запуск: python main.py --token=ТОКЕН")
        sys.exit(1)
        
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    dp.include_router(router)
    dp.include_router(adapter_router)

    if DEBUG_MODE:
        print("🤖 Бот запущен в режиме DEBUG...")
    else:
        print("🤖 Бот успешно запущен...")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
