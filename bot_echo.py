import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден в .env файле!")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Привет! Бот работает!")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"🔊 Вы сказали: {message.text}")

async def main():
    print("Бот-эхо запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
