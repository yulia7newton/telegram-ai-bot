import nest_asyncio
import asyncio
import random
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

nest_asyncio.apply()

TOKEN = "8861478338:AAEyylNDKbmItVpL_cbAUcE5jr-oxHLmKuE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Клавиатура
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎲 Игра"), KeyboardButton(text="🧮 Пример")],
        [KeyboardButton(text="📖 Стих"), KeyboardButton(text="❓ Вопрос")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="ℹ️ Помощь")]
    ],
    resize_keyboard=True
)

# Хранение статистики
stats = {}

# База знаний (вопросы и ответы)
knowledge = {
    "привет": "Привет! Как дела? 😊",
    "как дела": "У меня всё отлично! А у тебя?",
    "что ты умеешь": "Я умею:\n- играть в угадайку\n- решать примеры\n- писать стихи\n- отвечать на вопросы",
    "кто тебя создал": "Меня создал студент для учебного проекта",
    "спасибо": "Пожалуйста! Обращайся 🤗",
    "пока": "До свидания! Возвращайся 😊",
    "как тебя зовут": "Меня зовут Бот-Помощник!",
    "сколько время": "Напиши /time",
    "какая сегодня дата": "Напиши /date",
    "помощь": "Напиши /help для списка команд"
}

# Стихи (короткие)
poems = [
    "Котик спит на батарее,\nСолнце светит веселее.\nЗа окном шумит апрель,\nВ дверь стучится к нам капель.",
    "Утро красит нежным светом,\nПросыпайтесь, люди, с этим.\nНовый день принес удачу,\nПусть решаются задачи!",
    "За окошком дождик льется,\nКто-то весело смеется.\nДаже в дождь нельзя скучать,\nНужно дело начинать!",
    "Учиться нужно каждый день,\nОткинув в сторону лень.\nЗнания — это наша сила,\nЧтоб жизнь красивою нам было!",
    "В мире столько интересного,\nДоброго и повседневного.\nУлыбнись и подбодри,\nСчастье в жизни сотвори!"
]

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in stats:
        stats[user_id] = {"games": 0, "wins": 0, "math": 0, "math_correct": 0}
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я бот-помощник. Вот что я умею:\n\n"
        "🎲 /game - угадай число от 1 до 10\n"
        "🧮 /math - решить математический пример\n"
        "📖 /poem - прочитать короткий стих\n"
        "❓ /ask [вопрос] - задать вопрос\n"
        "📊 /stats - моя статистика\n"
        "📅 /date - сегодняшняя дата\n"
        "🕐 /time - текущее время\n"
        "ℹ️ /help - помощь\n\n"
        "Или просто напиши вопрос!",
        reply_markup=keyboard
    )

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "📋 Список команд:\n\n"
        "/start - приветствие\n"
        "/game - игра 'Угадай число'\n"
        "/math - решить пример\n"
        "/poem - получить стих\n"
        "/ask [текст] - задать вопрос\n"
        "/stats - моя статистика\n"
        "/date - сегодняшняя дата\n"
        "/time - текущее время\n"
        "/info - о боте",
        parse_mode="Markdown"
    )

@dp.message(Command("info"))
async def info_cmd(message: types.Message):
    await message.answer(
        "🤖 Бот-помощник\n"
        "Версия 3.0\n"
        "Функции: игра, математика, стихи, ответы на вопросы\n"
        "Создан для учебного проекта"
    )

@dp.message(Command("date"))
async def date_cmd(message: types.Message):
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    await message.answer(f"📅 Сегодня: {today}")

@dp.message(Command("time"))
async def time_cmd(message: types.Message):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    await message.answer(f"🕐 Текущее время: {now}")

@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    user_id = message.from_user.id
    data = stats.get(user_id, {"games": 0, "wins": 0, "math": 0, "math_correct": 0})
    game_rate = data['wins'] / data['games'] * 100 if data['games'] > 0 else 0
    math_rate = data['math_correct'] / data['math'] * 100 if data['math'] > 0 else 0
    await message.answer(
        f"📊 Твоя статистика:\n\n"
        f"🎲 Игра в числа:\n"
        f"   Сыграно: {data['games']}\n"
        f"   Побед: {data['wins']}\n"
        f"   Процент: {game_rate:.0f}%\n\n"
        f"🧮 Математика:\n"
        f"   Решено примеров: {data['math']}\n"
        f"   Правильно: {data['math_correct']}\n"
        f"   Процент: {math_rate:.0f}%",
        parse_mode="Markdown"
    )

# --- ИГРА В ЧИСЛА ---

@dp.message(Command("game"))
async def game_cmd(message: types.Message):
    number = random.randint(1, 10)
    user_id = message.from_user.id
    if user_id not in stats:
        stats[user_id] = {"games": 0, "wins": 0, "math": 0, "math_correct": 0}
    stats[user_id]["games"] += 1
    stats[user_id]["current_game"] = number
    await message.answer(
        "🎲 Игра 'Угадай число'\n\n"
        "Я загадал число от 1 до 10.\n"
        "Попробуй угадать!\n\n"
        "Напиши число:",
        parse_mode="Markdown"
    )

# --- МАТЕМАТИКА ---

@dp.message(Command("math"))
async def math_cmd(message: types.Message):
    # Генерируем простой пример
    operators = ['+', '-', '*']
    op = random.choice(operators)
    if op == '+':
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        answer = a + b
    elif op == '-':
        a = random.randint(10, 50)
        b = random.randint(1, a)
        answer = a - b
    else:  # *
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        answer = a * b
    user_id = message.from_user.id
    if user_id not in stats:
        stats[user_id] = {"games": 0, "wins": 0, "math": 0, "math_correct": 0}
    stats[user_id]["math"] += 1
    stats[user_id]["current_math"] = answer
    await message.answer(
        f"🧮 Реши пример:\n\n"
        f"`{a} {op} {b} = ?```\n\n"
        f"Напиши ответ:",
        parse_mode="Markdown"
    )

# --- СТИХИ ---

@dp.message(Command("poem"))
async def poem_cmd(message: types.Message):
    poem = random.choice(poems)
    await message.answer(
        f"📖 Стих:\n\n"
        f"_{poem}_\n\n"
        f"❤️ Надеюсь, понравилось!",
        parse_mode="Markdown"
    )

# --- ОТВЕТЫ НА ВОПРОСЫ ---

@dp.message(Command("ask"))
async def ask_cmd(message: types.Message):
    question = message.text.replace("/ask", "").strip().lower()
    if not question:
        await message.answer(
            "❓ Как задать вопрос:\n\n"
            "Напиши: `/ask Твой вопрос`\n\n"
            "Пример: `/ask как дела?`",
            parse_mode="Markdown"
        )
        return
    # Поиск ответа в базе знаний
    answer = None
    for key in knowledge:
        if key in question:
            answer = knowledge[key]
            break
    if answer:
        await message.answer(f"❓ Вопрос: {question}\n\n💡 Ответ: {answer}")
    else:
        # Если не знает ответа
        responses = [
            "Интересный вопрос! Я ещё учусь отвечать на такие. Попробуй спросить что-то другое.",
            "Хороший вопрос! Пока я не знаю ответа, но обязательно выучу.",
            "Запиши вопрос, я передам создателю, чтобы он добавил ответ!"
        ]
        await message.answer(f"❓ Вопрос: {question}\n\n💡 Ответ: {random.choice(responses)}")

# --- ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ---

@dp.message()
async def answer(message: types.Message):
    user_id = message.from_user.id
    text = message.text.lower()
    # Обработка кнопок
    if text == "🎲 игра":
        await game_cmd(message)
    elif text == "🧮 пример":
        await math_cmd(message)
    elif text == "📖 стих":
        await poem_cmd(message)
    elif text == "❓ вопрос":
        await message.answer("Напиши /ask Твой вопрос")
    elif text == "📊 статистика":
        await stats_cmd(message)
    elif text == "ℹ️ помощь":
        await help_cmd(message)
    # Обработка игры
    elif "current_game" in stats.get(user_id, {}):
        try:
            guess = int(text)
            secret = stats[user_id]["current_game"]
            if guess == secret:
                stats[user_id]["wins"] += 1
                del stats[user_id]["current_game"]
                await message.answer(f"✅ Поздравляю! Ты угадал число {secret}!\n\nСыграем ещё? Напиши /game", parse_mode="Markdown")
            else:
                hint = "больше" if guess < secret else "меньше"
                await message.answer(f"❌ Не угадал! Загаданное число {hint}.\nПопробуй ещё раз!", parse_mode="Markdown")
        except ValueError:
            await message.answer("❓ Напиши число от 1 до 10!")
    # Обработка математики
    elif "current_math" in stats.get(user_id, {}):
        try:
            user_answer = int(text)
            correct_answer = stats[user_id]["current_math"]
            if user_answer == correct_answer:
                stats[user_id]["math_correct"] += 1
                await message.answer("✅ Правильно! Отличная работа!\n\nХочешь ещё пример? Напиши /math", parse_mode="Markdown")
            else:
                await message.answer(f"❌ Неправильно! Правильный ответ: {correct_answer}\n\nПопробуй ещё раз! Напиши /math", parse_mode="Markdown")
            del stats[user_id]["current_math"]
        except ValueError:
            await message.answer("❓ Напиши число (цифрами)!")
    # Обычный ответ (если просто написали текст)
    else:
        # Поиск в базе знаний
        found = False
        for key in knowledge:
            if key in text:
                await message.answer(knowledge[key])
                found = True
                break
        if not found:
            await message.answer(
                "😊 Я тебя слышу!\n\n"
                "Попробуй:\n"
                "🎲 /game - поиграть\n"
                "🧮 /math - решить пример\n"
                "📖 /poem - прочитать стих\n"
                "❓ /ask вопрос - спросить что-то\n\n"
                "Или просто напиши: привет, как дела, что ты умеешь"
            )

# Запуск
async def main():
    print("🤖 Бот запущен!")
    print("Доступные режимы: игра, математика, стихи, вопросы")
    await dp.start_polling(bot)

await main()
