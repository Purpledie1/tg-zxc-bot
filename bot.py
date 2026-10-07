import asyncio
import json
import logging
import os
import random

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Файл для хранения ID пользователей
USERS_FILE = "users.json"

# 28 zxc/Dota 2 вариаций сообщений
ZXC_MESSAGES = [
    "Привет, сладкий zxc демонёнок желаю тебе сегодня хорошего дня на миду!",
    "Доброе утро, гуль! Пора вставать и забирать свои +30 птс в миду.",
    "Просыпайся, дед инсайд. Твой мид сам себя не выиграет, удачного фарма сегодня!",
    "Утро начинается не с кофе, а с фп сфа. Удачи в пабликах, zxc-шник!",
    "Вставай, проклятый! Твой реквием уже заждался, хорошего дня и легких каток.",
    "Доброе утро! Пусть сегодня твои койлы летят прямо в цель, а враги сами ломают шмотки.",
    "Проснись и пой, демон! Время жать паузы после каждого килла. Отличного дня!",
    "Утречко! Надеюсь, сегодня ты не проиграешь мид пуджу. Удачных игр и +птс!",
    "Открывай глаза. Шэдоу рейд вкачан, крипы идут, пора доминировать на карте!",
    "Доброе утро, токсик! Пусть твоя аура страха заставляет врагов ливать еще на стадии драфтов.",
    "Без бруды не выловишь птсы из пруда. Доброе утро, пора плести паутину побед!",
    "Лешрак заждался тебя, пупсик. Вставай, время ломать тавера и лица!",
    "Доброе утро, мидер! Пусть твой крипстат сегодня будет идеальным, а ганги — только удачными.",
    "Просыпайся, тень! Твой койл по КД уже готов стирать вражеского мидера. Удачного дня!",
    "Утречко! Желаю сегодня идеального позиционирования, фри-фарма и ни единого ганга в спину.",
    "Вставай, киберспортсмен. Инт сам себя не выиграет, пора апать ранг!",
    "Доброе утро! Пусть сегодня Габен благословит тебя на 5 адекватных тиммейтов (ну ладно, хотя бы на 4).",
    "Проснись и пой! Пусть руна ДД всегда спавнится под твоей ногой, а победы идут стриком.",
    "Утро доброе! Желаю, чтобы саппорты пулили крипов, а курьера никто не убивал.",
    "Доброе утро, zxc-гений. Пусть твои финды собирают души еще до выхода крипов.",
    "Доброе утро, повелитель мида! Забирай пачку крипов, бери быстрый даггер и иди выносить карту.",
    "Утречко! Пусть сегодня вражеский трон падает быстрее, чем ты успеваешь сказать «ГГ».",
    "Хватит спать, машина! Твой нетворс сегодня должен расти быстрее, чем горит вражеский трон.",
    "Доброе утро! Пусть твой счет сегодня будет 20-0, а репорты летят только во врагов.",
    "Вставай, легенда! Время оформлять ферст блад на руне и писать «?» в общий чат.",
    "Утро начинается не с кофе, а с разбитых шмоток вражеского керри. Хорошего дня!",
    "Просыпайся, токсик. Пора мутить всех со старта и выигрывать игру в соло 1х9.",
    "Доброе утро, гений драфтов! Желаю сегодня закрывать врагов ластпиком и кайфовать на фри-фарме."
]

def load_users() -> set:
    """Загружает список ID пользователей из файла."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Ошибка при чтении users.json: {e}")
            return set()
    return set()

def save_users(users: set):
    """Сохраняет список ID пользователей в файл."""
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(users), f)
    except IOError as e:
        logging.error(f"Ошибка при сохранении users.json: {e}")

# Инициализируем бота, диспетчер и планировщик
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()
active_users = load_users()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    user_id = message.from_user.id
    
    if user_id not in active_users:
        active_users.add(user_id)
        save_users(active_users)
        logging.info(f"Новый пользователь добавлен: {user_id}")
        
    await message.answer(
        "Привет! 👋\n"
        "Теперь я буду желать тебе доброго утра каждый день в 07:00 (по Иркутску).\n\n"
        "Напиши «тест», чтобы проверить сообщение прямо сейчас!"
    )

@dp.message(F.text.lower() == "тест")
async def cmd_test(message: types.Message):
    """Обработчик для тестирования (присылает рандомное утреннее сообщение)."""
    msg = random.choice(ZXC_MESSAGES)
    await message.answer(msg)

async def send_good_morning():
    """Функция для рассылки рандомного утреннего сообщения всем пользователям."""
    users_to_notify = load_users()
    logging.info(f"Начинаю рассылку доброго утра для {len(users_to_notify)} пользователей.")
    
    for user_id in users_to_notify:
        try:
            msg = random.choice(ZXC_MESSAGES)
            await bot.send_message(chat_id=user_id, text=msg)
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        logging.error("Не задан BOT_TOKEN.")
        return

    # Настраиваем планировщик на 07:00 по часовому поясу Иркутска
    scheduler.add_job(send_good_morning, 'cron', hour=7, minute=0, timezone='Asia/Irkutsk')
    scheduler.start()
    
    logging.info("Бот запущен и планировщик активирован (рассылка в 07:00 Иркутск).")

    # Запускаем поллинг
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен вручную.")
