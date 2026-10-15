import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import start, practice, steps, quiz, bugs, code_view

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("1c_learning_bot")

async def main() -> None:
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        logger.error(
            "BOT_TOKEN не задан! Пожалуйста, укажите валидный токен бота в файле .env "
            "или передайте через переменную окружения BOT_TOKEN."
        )
        sys.exit(1)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers in priority order
    dp.include_router(practice.router)
    dp.include_router(start.router)
    dp.include_router(steps.router)
    dp.include_router(quiz.router)
    dp.include_router(bugs.router)
    dp.include_router(code_view.router)

    logger.info("Запуск Telegram-бота обучения 1С...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")
