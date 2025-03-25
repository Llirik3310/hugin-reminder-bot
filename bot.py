
import asyncio
import logging
import json
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold

import os

API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher(storage=MemoryStorage())

reminders = []

def load_reminders():
    global reminders
    try:
        with open("reminders.json", "r") as f:
            reminders = json.load(f)
    except FileNotFoundError:
        reminders = []

def save_reminders():
    with open("reminders.json", "w") as f:
        json.dump(reminders, f)

@dp.message(commands=["start"])
async def cmd_start(message: Message):
    await message.answer("Привет, я Хугин 🐦\nЯ помогу тебе не забыть важное.\n\nКоманды:\n/add — добавить напоминание\n/list — список событий")

@dp.message(commands=["add"])
async def cmd_add(message: Message):
    await message.answer("Напиши напоминание в формате:\n`26.03.2025 17:00 Позвонить Ане`")

@dp.message()
async def process_message(message: Message):
    if len(message.text.split(" ")) >= 3 and message.text[:10].count(".") == 2:
        try:
            parts = message.text.split(" ", 2)
            date_str, time_str, text = parts
            remind_at = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
            reminders.append({
                "chat_id": message.chat.id,
                "text": text,
                "time": remind_at.strftime("%Y-%m-%d %H:%M")
            })
            save_reminders()
            await message.answer(f"Запомнил! Напомню {date_str} в {time_str} 🕒")
        except Exception:
            await message.answer("Неверный формат. Попробуй ещё раз.")
    else:
        await message.answer("Я не понял. Используй /add для создания напоминания.")

@dp.message(commands=["list"])
async def cmd_list(message: Message):
    user_reminders = [r for r in reminders if r["chat_id"] == message.chat.id]
    if not user_reminders:
        await message.answer("У тебя пока нет активных напоминаний.")
        return
    msg = "\n".join([f"{r['time']} — {r['text']}" for r in user_reminders])
    await message.answer(f"Твои напоминания:\n{msg}")

async def reminder_loop():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        to_send = [r for r in reminders if r["time"] == now]
        for r in to_send:
            try:
                await bot.send_message(r["chat_id"], f"🔔 Напоминание: {r['text']}")
                reminders.remove(r)
                save_reminders()
            except Exception as e:
                print("Ошибка отправки:", e)
        await asyncio.sleep(60)

async def main():
    load_reminders()
    asyncio.create_task(reminder_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
