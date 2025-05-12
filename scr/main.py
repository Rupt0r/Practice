import asyncio
import json
import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

API_TOKEN = '7284196933:AAHLKYUaA38WBQ_OVTaViJ0k_EFFb6mKVp4'
ADMIN_ID = 1110861387

router = Router()
users = set()

def load_models():
    path = "data/models.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.message(Command("start"))
async def cmd_start(message: Message):
    users.add(message.from_user.id)
    await message.answer("Привет! Я бот-помощник по 3D-картам корпусов университета.\n"
                         "Команды: /корпуса /галерея /новости /ресурсы /помощь")

@router.message(Command("помощь"))
async def cmd_help(message: Message):
    await message.answer("/корпуса — список корпусов\n/галерея — изображения\n"
                         "/новости — прогресс проекта\n/ресурсы — полезные ссылки")

@router.message(Command("корпуса"))
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
async def cmd_gallery(message: Message):
    models = load_models()
    for model in models.values():
        img_path = model.get("image")
        if img_path and os.path.exists(img_path):
            with open(img_path, "rb") as img:
                await message.answer_photo(img, caption=model["description"])

@router.message(Command("новости"))
async def cmd_news(message: Message):
    await message.answer("📰 Новости проекта:\n1. Создан корпус A\n2. Добавлен корпус B\n3. Интеграция с 2ГИС")

@router.message(Command("ресурсы"))
async def cmd_resources(message: Message):
    await message.answer("🔗 Полезные ссылки:\n- https://2gis.ru\n- https://mospolytech.ru")

@router.message(Command("статистика"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(f"Всего пользователей: {len(users)}")

@router.message(Command("добавить"))
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
    print('Я покакал')
    asyncio.run(main())
