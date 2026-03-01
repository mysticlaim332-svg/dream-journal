"""
Dream & Idea Journal — Telegram Bot
Entry point. Runs bot polling + FastAPI server concurrently in one process.
"""
import asyncio
import logging
import os

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from api import app as fastapi_app
from config import config
from handlers import start, voice, text
from services.scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

API_PORT = int(os.getenv("PORT", "8000"))


async def run_bot() -> None:
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(voice.router)
    dp.include_router(text.router)

    await setup_scheduler(bot)
    logger.info("Bot polling started")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def run_api() -> None:
    server_config = uvicorn.Config(
        fastapi_app,
        host="0.0.0.0",
        port=API_PORT,
        log_level="warning",
        loop="asyncio",
    )
    server = uvicorn.Server(server_config)
    logger.info(f"API server starting on port {API_PORT}")
    try:
        await server.serve()
    except OSError as e:
        logger.warning(f"API server could not start (port {API_PORT} busy?): {e}")
        logger.warning("Bot will run without Mini App API — this is fine for local testing")


async def main() -> None:
    await asyncio.gather(run_bot(), run_api())


if __name__ == "__main__":
    asyncio.run(main())
