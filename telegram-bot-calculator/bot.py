# мой первый тг бот - калькулятор
# делает математику через кнопки или текстом
# юзаю aiogram 3

import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

# логи чтоб видеть если че сломалось
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# токен берем из .env файла (ВАЖНО: не пушить его в гит!!!)
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("ОШИБКА: нет токена в .env файле! Создай .env и напиши BOT_TOKEN=твой_токен")
    exit()

bot = Bot(token=TOKEN)
dp = Dispatcher()

# тут храним что юзер ввел (выражение)
memory = {}  # user_id -> строка с выражением


def build_kb():
    """собирает клавиатуру с кнопками"""
    btn_row1 = [
        InlineKeyboardButton(text="7", callback_data="7"),
        InlineKeyboardButton(text="8", callback_data="8"),
        InlineKeyboardButton(text="9", callback_data="9"),
        InlineKeyboardButton(text="/", callback_data="/"),
    ]
    btn_row2 = [
        InlineKeyboardButton(text="4", callback_data="4"),
        InlineKeyboardButton(text="5", callback_data="5"),
        InlineKeyboardButton(text="6", callback_data="6"),
        InlineKeyboardButton(text="*", callback_data="*"),
    ]
    btn_row3 = [
        InlineKeyboardButton(text="1", callback_data="1"),
        InlineKeyboardButton(text="2", callback_data="2"),
        InlineKeyboardButton(text="3", callback_data="3"),
        InlineKeyboardButton(text="-", callback_data="-"),
    ]
    btn_row4 = [
        InlineKeyboardButton(text="0", callback_data="0"),
        InlineKeyboardButton(text=".", callback_data="."),
        InlineKeyboardButton(text="=", callback_data="="),
        InlineKeyboardButton(text="+", callback_data="+"),
    ]
    btn_row5 = [
        InlineKeyboardButton(text="⌫", callback_data="back"),
        InlineKeyboardButton(text="C", callback_data="clear"),
    ]
    kb = InlineKeyboardMarkup(
        inline_keyboard=[btn_row1, btn_row2, btn_row3, btn_row4, btn_row5]
    )
    return kb


@dp.message(Command("start"))
async def start(message: types.Message):
    """команда старт - показываем калькулятор"""
    user_id = message.from_user.id
    memory[user_id] = ""  # обнуляем
    await message.answer(
        "Йо! Это калькулятор в телеге\n"
        "жмакай по кнопкам или пиши пример текстом\n"
        "например: 2+2*3\n"
        "можно скобки и степени (2**3)",
        reply_markup=build_kb()
    )


@dp.message()
async def text_handler(message: types.Message):
    """если юзер написал текст - вычисляем"""
    text = message.text.strip()
    uid = message.from_user.id

    if uid not in memory:
        memory[uid] = ""

    # если написал очистить
    if text.lower() in ("c", "clear", "очистить"):
        memory[uid] = ""
        await message.answer("ок, очистил", reply_markup=build_kb())
        return

    # считаем
    res = calc(text)
    await message.answer(f"{text} = {res}", reply_markup=build_kb())


@dp.callback_query()
async def btn_click(callback: types.CallbackQuery):
    """когда юзер жмет на кнопку"""
    uid = callback.from_user.id
    data = callback.data

    if uid not in memory:
        memory[uid] = ""

    # очистить все
    if data == "clear":
        memory[uid] = ""
        await callback.message.edit_text("очищено", reply_markup=build_kb())
        await callback.answer()
        return

    # стереть последний символ
    if data == "back":
        memory[uid] = memory[uid][:-1]
        display = memory[uid] if memory[uid] else "0"
        await callback.message.edit_text(f"📝 {display}", reply_markup=build_kb())
        await callback.answer()
        return

    # посчитать результат
    if data == "=":
        expr = memory[uid]
        if not expr:
            await callback.answer("ничего не ввел еще")
            return
        res = calc(expr)
        memory[uid] = str(res)
        await callback.message.edit_text(f"{expr} = {res}", reply_markup=build_kb())
        await callback.answer()
        return

    # добавляем символ к выражению
    memory[uid] += data
    await callback.message.edit_text(f"📝 {memory[uid]}", reply_markup=build_kb())
    await callback.answer()


def calc(expr):
    """
    вычисляет выражение безопасно
    проверяем что там только цифры и операции чтоб нельзя было взломать
    """
    if not expr.strip():
        return "0"

    # разрешенные символы (безопасность!)
    allowed = "0123456789+-*/().% "
    for ch in expr:
        if ch not in allowed:
            return "ошибка: можно только цифры и + - * / ( )"

    try:
        # eval с ограничениями - безопасно
        res = eval(expr, {"__builtins__": {}}, {})
        if type(res) in (int, float):
            if res == int(res):
                return str(int(res))
            return f"{res:.8f}".rstrip("0").rstrip(".")
        return "ошибка"
    except ZeroDivisionError:
        return "на ноль делить нельзя!"
    except SyntaxError:
        return "ошибка в выражении, проверь скобки"
    except Exception as e:
        return f"ошибка: {e}"


async def main():
    print("бот запущен! жмякни /start")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
