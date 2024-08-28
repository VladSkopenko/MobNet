import asyncio
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from telegram_app.handlers.user_privat import user_private_router

load_dotenv()

TOKEN = "7534910544:AAH3RBd3_r1LhmYtnX-nHMaCVbYXpOUGexM"
default = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=TOKEN, default=default)
dp = Dispatcher()

dp.include_router(user_private_router)


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="Запустити бота"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
