
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from datetime import datetime, timedelta
import json

API_TOKEN = "YOUR_API_TOKEN_HERE"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

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

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Привет, я Хугин 🐦\nЯ помогу тебе не забыть важное.\n\nКоманды:\n/add — добавить напоминание\n/list — список событий")

@dp.message_handler(commands=["add"])
async def add_reminder(message: types.Message):
    await message.reply("Напиши напоминание в формате:\n`14.04.2025 15:00 Позвонить Ане`", parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(lambda message: message.text and message.text[:10].count(".") == 2)
async def save_user_reminder(message: types.Message):
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
        await message.reply(f"Запомнил! Напомню {date_str} в {time_str} 🕒")
    except Exception as e:
        await message.reply("Неверный формат. Попробуй ещё раз.")

@dp.message_handler(commands=["list"])
async def list_reminders(message: types.Message):
    user_reminders = [r for r in reminders if r["chat_id"] == message.chat.id]
    if not user_reminders:
        await message.reply("У тебя пока нет активных напоминаний.")
        return
    msg = "\n".join([f"{r['time']} — {r['text']}" for r in user_reminders])
    await message.reply(f"Твои напоминания:\n{msg}")

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

if __name__ == "__main__":
    load_reminders()
    loop = asyncio.get_event_loop()
    loop.create_task(reminder_loop())
    executor.start_polling(dp, skip_updates=True)
