import os
from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from handlers.user_privat import user_private_router
from utils.py_logger import get_logger

TOKEN = os.environ.get("TELEGRAM_TOKEN")
default = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=TOKEN, default=default)
dp = Dispatcher()
logger = get_logger(__name__)
dp.include_router(user_private_router)


async def get_webhook_path() -> str:
    WEBHOOK_URL = f"dragon-top-greatly.ngrok-free.app"
    logger.debug(f"WEBHOOK_URL: {WEBHOOK_URL}")
    return WEBHOOK_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url=await get_webhook_path(), drop_pending_updates=True)  # noqa
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
