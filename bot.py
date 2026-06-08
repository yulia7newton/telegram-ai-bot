import nest_asyncio
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove
import requests
import json
import time
import os
from dotenv import load_dotenv

nest_asyncio.apply()
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
user_histories = {}
MAX_HISTORY = 5
WORKING_MODEL = None

def get_available_free_models():
    """Получает список всех доступных бесплатных моделей"""
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=30
        )
        if response.status_code == 200:
            models = response.json()
            free_models = []
            for model in models.get("data", []):
                model_id = model.get("id", "")
                if ":free" in model_id:
                    free_models.append(model_id)
            return free_models
        return []
    except Exception as e:
        print(f"Ошибка: {e}")
        return []

def find_working_model(free_models):
    """Находит первую работающую модель"""
    print("🔍 Поиск работающей модели...")

    # Приоритетные модели (которые точно возвращают текст)
    priority_models = [
        "qwen/qwen3-coder:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free"
    ]

    # Сначала проверяем приоритетные
    for model in priority_models:
        if model in free_models:
            print(f"  Проверяем приоритетную модель: {model}")
            if test_model(model):
                return model

    # Затем все остальные
    for model in free_models:
        if model not in priority_models:
            print(f"  Проверяем: {model}")
            if test_model(model):
                return model

    return None

def test_model(model):
    """Тестирует модель простым запросом"""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Скажи 'ok'"}],
                "max_tokens": 10,
            },
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            # Пробуем извлечь ответ разными способами
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                content = message.get("content", "")

                # Если ответ пустой, возможно это safety-объект
                if content:
                    print(f"    ✅ Модель работает: {model}")
                    return True
                else:
                    print(f"    ⚠️ Модель {model} вернула пустой ответ")
                    return False
        else:
            print(f"    ❌ Модель {model} не работает: {response.status_code}")
        return False
    except Exception as e:
        print(f"    ❌ Ошибка: {model} - {e}")
        return False

def extract_response(response_data):
    """Извлекает текст ответа из разных форматов OpenRouter"""
    try:
        # Стандартный формат
        if "choices" in response_data and len(response_data["choices"]) > 0:
            message = response_data["choices"][0].get("message", {})
            content = message.get("content", "")
            if content:
                return content
        # Если ответ в другом формате
        if "candidates" in response_data:
            for candidate in response_data["candidates"]:
                if "content" in candidate:
                    parts = candidate["content"].get("parts", [])
                    for part in parts:
                        if "text" in part and part["text"]:
                            return part["text"]

        # Если ничего не нашли
        print(f"Не удалось извлечь ответ из: {json.dumps(response_data, indent=2)}")
        return None

    except Exception as e:
        print(f"Ошибка извлечения ответа: {e}")
        return None

def get_ai_response(user_id: int, message_text: str) -> str:
    """Отправляет запрос к модели и возвращает ответ"""
    global WORKING_MODEL

    if WORKING_MODEL is None:
        return "❗️ Бот ещё не инициализирован. Напишите /start"

    try:
        if user_id not in user_histories:
            user_histories[user_id] = [
                {"role": "system", "content": "Ты полезный помощник. Отвечай на русском языке кратко."}
            ]

        user_histories[user_id].append({"role": "user", "content": message_text})

        if len(user_histories[user_id]) > MAX_HISTORY * 2 + 1:
            user_histories[user_id] = [user_histories[user_id][0]] + user_histories[user_id][-MAX_HISTORY * 2:]

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": WORKING_MODEL,
                "messages": user_histories[user_id],
                "temperature": 0.7,
                "max_tokens": 1000,
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()

            # Извлекаем ответ
            answer = extract_response(result)

            if answer:
                user_histories[user_id].append({"role": "assistant", "content": answer})
                return answer
            else:
                # Если не удалось извлечь ответ, показываем что получили
                return f"⚠️ Получен странный ответ от модели. Попробуйте другую командой /reload"
        else:
            error_text = response.text[:200]
            return f"❗️ Ошибка API ({response.status_code}): {error_text}"

    except requests.exceptions.Timeout:
        return "⏰ Таймаут. Попробуйте ещё раз."
    except Exception as e:
        print(f"Ошибка: {e}")
        return "❗️ Извините, произошла ошибка."

@dp.message(Command("start"))
async def start_command(message: types.Message):
    global WORKING_MODEL

    await message.answer(
        "🔍 Инициализация бота...\n\n"
        "Поиск работающей модели...",
        reply_markup=ReplyKeyboardRemove()
    )

    free_models = get_available_free_models()
    WORKING_MODEL = find_working_model(free_models)

    if WORKING_MODEL:
        await message.answer(
            f"✅ Бот готов!\n\n"
            f"Модель: {WORKING_MODEL}\n\n"
            "Просто напиши мне сообщение!\n\n"
            "📌 Команды:\n"
            "/clear — очистить историю\n"
            "/reload — перезагрузить модель"
        )
    else:
        await message.answer("❗️ Не удалось найти работающую модель. Попробуйте позже.")

@dp.message(Command("clear"))
async def clear_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_histories:
        user_histories[user_id] = [
            {"role": "system", "content": "Ты полезный помощник. Отвечай на русском языке кратко."}
        ]
    await message.answer("🧹 История очищена!")

@dp.message(Command("reload"))
async def reload_command(message: types.Message):
    global WORKING_MODEL

    await message.answer("🔄 Перезагрузка модели...")

    free_models = get_available_free_models()
    new_model = find_working_model(free_models)

    if new_model:
        WORKING_MODEL = new_model
        await message.answer(f"✅ Модель обновлена: {WORKING_MODEL}")
    else:
        await message.answer("❗️ Не найдено работающей модели.")

@dp.message()
async def chat_with_ai(message: types.Message):
    if WORKING_MODEL is None:
        await message.answer("❗️ Бот ещё не готов. Напишите /start")
        return

    await bot.send_chat_action(message.chat.id, action="typing")
    response = get_ai_response(message.from_user.id, message.text)
    await message.answer(response)

async def main():
    print("🚀 Бот запущен!")
    print("📌 Напишите /start для инициализации")
    await dp.start_polling(bot)

await main()
