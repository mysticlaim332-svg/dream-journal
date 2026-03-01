"""
/start command — register user and show welcome message.
"""
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import database
import keyboards
from services import scheduler

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = await database.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    name = message.from_user.first_name or "друже"
    await message.answer(
        f"🌙 *Привіт, {name}!*\n\n"
        "Це твій особистий журнал снів та ідей.\n\n"
        "Просто надішли:\n"
        "🎙 *Голосове* — і я транскрибую та проаналізую\n"
        "✍️ *Текст* — опиши сон або ідею словами\n\n"
        "Вранці я нагадаю тобі записати сон 🌅",
        parse_mode="Markdown",
        reply_markup=keyboards.main_menu(message.from_user.id),
    )


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    user = await database.get_user(message.from_user.id)
    if not user:
        await message.answer("Спочатку напиши /start")
        return

    await message.answer(
        "⚙️ *Налаштування*\n\n"
        f"🔔 Нагадування: {'увімкнено' if user['notifications_enabled'] else 'вимкнено'}\n"
        f"🕐 Час: {user['notification_time'][:5]}\n"
        f"🌐 Мова: {user['language'].upper()}",
        parse_mode="Markdown",
        reply_markup=keyboards.settings_keyboard(user["notifications_enabled"]),
    )


@router.message(lambda m: m.text == "⚙️ Налаштування")
async def btn_settings(message: Message) -> None:
    await cmd_settings(message)


@router.callback_query(lambda c: c.data == "settings:toggle_notifications")
async def toggle_notifications(callback: CallbackQuery, bot) -> None:
    user = await database.get_user(callback.from_user.id)
    new_state = not user["notifications_enabled"]
    updated = await database.update_user(
        callback.from_user.id,
        {"notifications_enabled": new_state},
    )

    if new_state:
        scheduler.reschedule_user(bot, updated)
        text = "🔔 Нагадування *увімкнено*"
    else:
        scheduler.cancel_user(callback.from_user.id)
        text = "🔕 Нагадування *вимкнено*"

    await callback.answer(text, show_alert=False)
    await callback.message.edit_reply_markup(
        reply_markup=keyboards.settings_keyboard(new_state)
    )


@router.callback_query(lambda c: c.data == "settings:set_time")
async def set_time_prompt(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "⏰ Надішли час у форматі *ГГ:ХХ*\n"
        "Наприклад: `07:30` або `08:00`",
        parse_mode="Markdown",
    )
