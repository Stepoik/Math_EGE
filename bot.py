import aiogram.utils.exceptions
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
from sql_connect import Database
import random

API_TOKEN = "<API>"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

users_db = Database("db.sqlite3", "roflobot_sessions")
tasks_db = Database("db.sqlite3", "task_math")

menu_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_kb.add(types.KeyboardButton("📖 Ботать"))
menu_kb.add(types.KeyboardButton("❓ Помощь"))

next_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
next_kb.add(types.KeyboardButton("➡️ Другое задание"))
next_kb.add(types.KeyboardButton("⏹ Выйти в меню"))

ege_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
task = 0
range_tasks = 6
for i in range(0, 3):
    tasks = []
    for j in range(1, 7):
        tasks.append(types.KeyboardButton(str(range_tasks * i + j)))
    ege_kb.row(*tasks)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    info = users_db.select({"chat_id": message.chat.id})
    if len(info) == 0:
        await message.answer("Добро пожаловать", reply_markup=menu_kb)
        users_db.insert({"chat_id": message.chat.id})


@dp.message_handler(commands=["menu"])
async def menu(message: types.Message):
    clear_session(message)
    await message.answer("Меню", reply_markup=menu_kb)


async def start_solve(message: types.Message):
    clear_session(message)
    await message.answer("Выберите задание:", reply_markup=ege_kb)
    users_db.update({"session_type": "Solve", "session_stage": "1"}, {"chat_id": message.chat.id})


async def send_task(message: types.Message):
    user_info = users_db.select({"chat_id": message.chat.id})[0]
    if user_info[5] != "null" and user_info[5] is not None:
        task_num = user_info[5]
    else:
        task_num = message.text
    info = tasks_db.select({"ege_id": task_num})
    if len(info) == 0:
        await message.answer("Неверный номер", reply_markup=menu_kb)
        clear_session(message)
        return
    task_info = random.choice(info)
    photo = InputFile(rf"C:\Users\Service\Desktop\answers\{task_info[5]}")
    await bot.send_photo(message.chat.id, photo=photo, reply_markup=next_kb)
    users_db.update({"task_id": task_info[0], "session_stage": "2", "task_ege_id": f"{task_num}"},
                    {"chat_id": message.chat.id})


async def check_answer(message: types.Message):
    answer = message.text
    user_info = users_db.select({"chat_id": message.chat.id})[0]
    if user_info[4] != "null":
        task_info = tasks_db.select({"id": user_info[4]})[0]
        if str(task_info[7]) == str(answer):
            await message.answer("Верно", reply_markup=next_kb)
        else:
            if task_info[1] >= 12:
                text = "Проверьте себя"
            else:
                text = "Неверно"
            photo = InputFile(rf"C:\Users\Service\Desktop\answers\answers\{task_info[0]}.png")
            await bot.send_photo(message.chat.id, photo, text, reply_markup=next_kb)
        users_db.update({"task_id":"null"}, {"chat_id": message.chat.id})


def clear_session(message: types.Message):
    chat_id = message.chat.id
    users_db.update({"session_type": "null", "session_stage": "null", "task_id": "null", "task_ege_id":"null"}, {"chat_id": chat_id})

@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    clear_session(message)
    await message.answer("Помощь", reply_markup=menu_kb)

@dp.message_handler()
async def message_processing(message: types.Message):
    text = message.text
    if text == "📖 Ботать":
        await start_solve(message)
    elif text == "➡️ Другое задание":
        await send_task(message)
    elif text == "⏹ Выйти в меню":
        await menu(message)
    elif text == "❓ Помощь":
        await help(message)
    else:
        info = users_db.select({"chat_id": message.chat.id})
        if len(info) == 0:
            await start(message)
            return
        user_info = info[0]
        if user_info[2] == "Solve":
            if user_info[3] == 1:
                await send_task(message)
            elif user_info[3] == 2:
                await check_answer(message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
