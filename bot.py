import asyncio
import random
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile, ChatPermissions
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "8282317538:AAHVMpbd4E5C_YjdICd0KES_TW3_4taMyy4"
OWNER_ID = 6930148555
CHAT_ID = -1003887218129
THREAD_ID = 472
PHOTO_PATH = "баннер.jpg"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

auto_sending = True
sent_count = 0

class BroadcastState(StatesGroup):
    waiting_text = State()

class PinState(StatesGroup):
    waiting_text = State()

NAMES = [
    "беленький кот^^", "Andr", "бисквит", "Marlboro", "Dilarrra",
    "ewz | darkness", "Homa", "exxzee", "Артём", "Forever young",
    "Hutma", "Movladi", "Муська", "Аноним", "Asymmetrical | st2",
    "Andrey Neuron", "priora2", "$lava", "варькаа",
    "Narek Venom", "Дана Малкина", "†ХАЗБИК†",
    "Хочу бордер коооли", "котик | Elkey", "Платон", "r66in", "омагад",
    "Tihon", "аня", "Утка:)", "Rty Yw", "Ксюша",
    "kamidanat", "kitten", "Chel Kakoyto", "Лёха",
    "Дреем", "Рахматулла", "крутая", "Vitya", "Bladislav Enduro",
    "Gulija Pinguini", "Бизнес мяу", "Rita", "twwerti", "Максим",
    "KDN", "Екатерина Данилова", "1s0y"
]

TON_RANGES = [
    (3.0, 8.0, 50),
    (8.0, 15.0, 30),
    (15.0, 25.0, 15),
    (25.0, 30.0, 5),
]

def get_random_ton() -> float:
    ranges = [r[:2] for r in TON_RANGES]
    weights = [r[2] for r in TON_RANGES]
    chosen = random.choices(ranges, weights=weights, k=1)[0]
    return round(random.uniform(chosen[0], chosen[1]), 2)

def main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="▶️ Старт авто", callback_data="start_auto")
    kb.button(text="⏹ Стоп авто", callback_data="stop_auto")
    kb.button(text="📤 Отправить сейчас", callback_data="send_now")
    kb.button(text="📢 Рассылка в топик", callback_data="broadcast")
    kb.button(text="📌 Закрепить сообщение", callback_data="pin_msg")
    kb.button(text="🔇 Замутить чат", callback_data="mute_chat")
    kb.button(text="🔊 Размутить чат", callback_data="unmute_chat")
    kb.button(text="📊 Статистика", callback_data="stats")
    kb.button(text="🎲 Рандом имя", callback_data="random_name")
    kb.button(text="💰 Рандом TON", callback_data="random_ton")
    kb.button(text="📋 Список имён", callback_data="names_list")
    kb.adjust(2)
    return kb.as_markup()

def back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Назад", callback_data="back_menu")
    kb.adjust(1)
    return kb.as_markup()

async def send_profit():
    global sent_count
    name = random.choice(NAMES)
    ton = get_random_ton()
    caption = (
        f"🚀 <b>НОВЫЙ ПРОФИТ!</b>\n\n"
        f"👤 Пользователь: <b>{name}</b>\n"
        f"💰 Сумма: <b>{ton} TON</b>\n\n"
        f"🎊 Поздравляем с успешной сделкой! 💎"
    )
    try:
        if os.path.exists(PHOTO_PATH):
            photo = FSInputFile(PHOTO_PATH)
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=photo,
                caption=caption,
                parse_mode="HTML",
                message_thread_id=THREAD_ID
            )
        else:
            print(f"⚠️ Фото не найдено: {PHOTO_PATH}, отправляю текстом")
            await bot.send_message(
                chat_id=CHAT_ID,
                text=caption,
                parse_mode="HTML",
                message_thread_id=THREAD_ID
            )
        sent_count += 1
        print(f"✅ [{sent_count}] {name} — {ton} TON")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

async def auto_loop():
    while True:
        if auto_sending:
            await send_profit()
            delay = random.randint(300, 600)
            print(f"⏳ Следующее через {delay//60}м {delay%60}с")
            await asyncio.sleep(delay)
        else:
            await asyncio.sleep(10)

def menu_text():
    status = "✅ Работает" if auto_sending else "⏹ Остановлен"
    return (
        f"👑 <b>LOGBOT — Панель управления</b>\n\n"
        f"🤖 Авто-отправка: {status}\n"
        f"📨 Отправлено: <b>{sent_count}</b>\n\n"
        f"Выбери действие 👇"
    )

@dp.message(CommandStart())
async def start(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    await message.answer(menu_text(), parse_mode="HTML", reply_markup=main_kb())

@dp.callback_query(F.data == "back_menu")
async def back_menu(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != OWNER_ID:
        return
    await state.clear()
    try:
        await call.message.edit_text(menu_text(), parse_mode="HTML", reply_markup=main_kb())
    except:
        await call.message.answer(menu_text(), parse_mode="HTML", reply_markup=main_kb())

@dp.callback_query(F.data == "start_auto")
async def cb_start_auto(call: CallbackQuery):
    if call.from_user.id != OWNER_ID: return
    global auto_sending
    auto_sending = True
    await call.answer("▶️ Авто-отправка запущена!", show_alert=True)

@dp.callback_query(F.data == "stop_auto")
async def cb_stop_auto(call: CallbackQuery):
    if call.from_user.id != OWNER_ID: return
    global auto_sending
    auto_sending = False
    await call.answer("⏹ Авто-отправка остановлена!", show_alert=True)

@dp.callback_query(F.data == "send_now")
async def cb_send_now(call: CallbackQuery):
    if call.from_user.id != OWNER_ID: return
    await send_profit()
    await call.answer("📤 Отправлено!", show_alert=True)

@dp.callback_query(F.data == "broadcast")
async def cb_broadcast(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != OWNER_ID: return
    await state.set_state(BroadcastState.waiting_text)
    await call.message.edit_text(
        "📢 <b>Рассылка</b>\n\nНапиши текст — отправлю в топик:",
        parse_mode="HTML", reply_markup=back_kb()
    )

@dp.message(BroadcastState.waiting_text)
async def do_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != OWNER_ID: return
    try:
        await bot.send_message(
            chat_id=CHAT_ID, text=message.text,
            parse_mode="HTML", message_thread_id=THREAD_ID
        )
        await message.answer("✅ Отправлено!", reply_markup=main_kb())
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}", reply_markup=main_kb())
    await state.clear()

@dp.callback_query(F.data == "pin_msg")
async def cb_pin(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != OWNER_ID: return
    await state.set_state(PinState.waiting_text)
    await call.message.edit_text(
        "📌 <b>Закрепить</b>\n\nНапиши текст для закрепления:",
        parse_mode="HTML", reply_markup=back_kb()
    )

@dp.message(PinState.waiting_text)
async def do_pin(message: Message, state: FSMContext):
    if message.from_user.id != OWNER_ID: return
    try:
        sent = await bot.send_message(
            chat_id=CHAT_ID, text=message.text,
            parse_mode="HTML", message_thread_id=THREAD_ID
        )
        await bot.pin_chat_message(chat_id=CHAT_ID, message_id=sent.message_id)
        await message.answer("✅ Закреплено!", reply_markup=main_kb())
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}", reply_markup=main_kb())
    await state.clear()

@dp.callback_query(F.data == "mute_chat")
async def cb_mute(call: CallbackQuery):
    if call.from_user.id != OWNER_ID: return
    try:
        await bot.set_chat_permissions(
            chat_id=CHAT_ID,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await call.answer("🔇 Чат замучен!", show_alert=True)
    except Exception as e:
        await call.answer(f"❌ {e}", show_alert=True)

@dp.callback_query(F.data == "unmute_chat")
async def cb_unmute(call: CallbackQuery):
    if call.from_user.id != OWNER_ID: return
    try:
        await bot.set_chat_permissions(
            chat_id=CHAT_ID,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
        await call.answer("🔊 Чат размучен!", show_alert=True)
    except Exception as e:
        await call.answer(f"❌ {e}", show_alert=True)

@dp.callback_query(F.data == "stats")
async def cb_stats(call: CallbackQuery):
    if call.from_user.id != OWNER_ID: return
    status = "✅ Работает" if auto_sending else "⏹ Остановлен"
    await call.message.edit_text(
        f"📊 <b>Статистика</b>\n\n"
        f"📨 Отправлено профитов: <b>{sent_count}</b>\n"
        f"🤖 Авто-отправка: {status}\n"
        f"👥 Имён в базе: <b>{len(NAMES)}</b>",
        parse_mode="HTML", reply_markup=back_kb()
    )

@dp.callback_query(F.data == "random_name")
async def cb_random_name(call: CallbackQuery):
    if call.from_user.id != OWNER_ID: return
    await call.answer(f"🎲 {random.choice(NAMES)}", show_alert=True)

@dp.callback_query(F.data == "random_ton")
async def cb_random_ton(call: CallbackQuery):
    if call.from_user.id != OWNER_ID: return
    await call.answer(f"💰 {get_random_ton()} TON", show_alert=True)

@dp.callback_query(F.data == "names_list")
async def cb_names_list(call: CallbackQuery):
    if call.from_user.id != OWNER_ID: return
    names_text = "\n".join([f"• {n}" for n in NAMES])
    await call.message.edit_text(
        f"📋 <b>Список имён ({len(NAMES)} шт.)</b>\n\n{names_text}",
        parse_mode="HTML", reply_markup=back_kb()
    )

@dp.message(Command("clear"))
async def cmd_clear(message: Message):
    if message.from_user.id != OWNER_ID: return
    args = message.text.split()
    count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
    deleted = 0
    for i in range(count):
        try:
            await bot.delete_message(chat_id=CHAT_ID, message_id=message.message_id - i)
            deleted += 1
        except:
            pass
    await message.answer(f"🗑 Удалено: {deleted}")

async def main():
    print("✦ LOGBOT запущен ✦")
    asyncio.create_task(auto_loop())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
