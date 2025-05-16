import asyncio
import json
import logging
import os
from functools import wraps

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import data.secret_data as sd

# Настройка логирования
logging.basicConfig(
    filename="data/bot.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def log_command(name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logging.info(f"{name}: active")
            result = await func(*args, **kwargs)
            logging.info(f"{name}: inactive")
            return result
        return wrapper
    return decorator


API_TOKEN = sd.SECRET_TOKEN
ADMIN_ID = sd.SECRET_ADMIN_ID

router = Router()
users = set()


def load_models():
    path = "data/models.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@router.message(Command("start"))
@log_command("start")
async def cmd_start(message: Message):
    users.add(message.from_user.id)
    await message.answer(
        "Привет! Я бот-помощник по 3D-картам корпусов университета.\n"
        "Команды: /корпуса /галерея /новости /ресурсы /помощь"
    )


@router.message(Command("помощь"))
@log_command("help")
async def cmd_help(message: Message):
    await message.answer(
        "/корпуса — список корпусов\n"
        "/галерея — изображения\n"
        "/новости — прогресс проекта\n"
        "/ресурсы — полезные ссылки"
    )


@router.message(Command("корпуса"))
@log_command("corpuses")
async def cmd_corpuses(message: Message):
    models = load_models()
    if not models:
        await message.answer("Нет доступных корпусов.")
        return
    text = "📍 Список корпусов:\n"
    for name, data in models.items():
        text += f"🔹 {name}: {data['description']}\n"
    await message.answer(text)


@router.message(Command("галерея"))
@log_command("gallery")
async def cmd_gallery(message: Message):
    models = load_models()
    for model in models.values():
        img_path = model.get("image")
        if img_path and os.path.exists(img_path):
            with open(img_path, "rb") as img:
                await message.answer_photo(img, caption=model["description"])


@router.message(Command("новости"))
@log_command("news")
async def cmd_news(message: Message):
    await message.answer(
        "📰 Новости проекта:\n"
        "1. Создан корпус A\n"
        "2. Добавлен корпус B\n"
        "3. Интеграция с 2ГИС"
    )


@router.message(Command("ресурсы"))
@log_command("resources")
async def cmd_resources(message: Message):
    await message.answer("🔗 Полезные ссылки:\n- https://2gis.ru\n- https://mospolytech.ru")


@router.message(Command("статистика"))
@log_command("stats")
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(f"Всего пользователей: {len(users)}")


@router.message(Command("добавить"))
@log_command("add")
async def cmd_add(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.replace("/добавить", "").strip().split(" | ")
    if len(args) != 3:
        await message.answer("Формат: /добавить Название | Описание | путь_к_изображению")
        return
    name, desc, img = args
    models = load_models()
    models[name] = {"description": desc, "image": img}
    with open("data/models.json", "w", encoding="utf-8") as f:
        json.dump(models, f, ensure_ascii=False, indent=2)
    await message.answer(f"✅ Добавлен корпус {name}")


async def main():
    bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)

    os.makedirs("data", exist_ok=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.info("BOT: active")
    asyncio.run(main())
