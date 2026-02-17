"""
Text message handler.
Handles typed dreams/ideas and menu button presses.
"""
import logging
import re
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database
import keyboards
from handlers.voice import process_entry, _detect_type

logger = logging.getLogger(__name__)
router = Router()


class SetTimeState(StatesGroup):
    waiting_for_time = State()


# ── Menu buttons ──────────────────────────────────────────────────────────────

@router.message(lambda m: m.text in ("🌙 Сон", "💡 Ідея"))
async def btn_entry_shortcut(message: Message) -> None:
    """Quick-record buttons: ask user to send voice or text next."""
    type_map = {"🌙 Сон": "dream", "💡 Ідея": "idea"}
    entry_type = type_map[message.text]
    label = "сон" if entry_type == "dream" else "ідею"
    await message.answer(
        f"Добре! Надішли голосове повідомлення або напиши свій {label} текстом.",
        parse_mode="Markdown",
    )


@router.message(lambda m: m.text == "📅 Мої записи")
async def btn_my_entries(message: Message) -> None:
    user = await database.get_user(message.from_user.id)
    if not user:
        await message.answer("Спочатку напиши /start")
        return

    entries = await database.get_user_entries(user["id"], limit=5)
    if not entries:
        await message.answer("У тебе ще немає записів. Надішли голосове або текст!")
        return

    keyboard = keyboards.history_keyboard(entries)
    await message.answer(
        f"📅 *Останні {len(entries)} записів:*",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


@router.callback_query(lambda c: c.data.startswith("entry:"))
async def show_entry(callback: CallbackQuery) -> None:
    entry_id = callback.data.split(":", 1)[1]
    db = database.get_db()
    result = (
        db.table("entries")
        .select("*, ai_analysis(*)")
        .eq("id", entry_id)
        .single()
        .execute()
    )
    entry = result.data
    if not entry:
        await callback.answer("Запис не знайдено")
        return

    await callback.answer()

    analysis = entry.get("ai_analysis") or {}
    type_emoji = {"dream": "🌙", "idea": "💡", "thought": "💭"}
    emoji = type_emoji.get(entry["type"], "📝")
    date = entry["created_at"][:16].replace("T", " ")

    lines = [
        f"{emoji} *{date}*",
        "",
        entry["raw_text"],
    ]
    if analysis:
        tags = " ".join(analysis.get("tags", []))
        lines += [
            "",
            f"📝 {analysis.get('summary', '')}",
            f"🏷 {tags}",
            f"💭 {analysis.get('emotional_tone', '')}",
        ]

    await callback.message.answer("\n".join(lines), parse_mode="Markdown")


# ── Time setting FSM ──────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "settings:set_time")
async def prompt_set_time(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.answer(
        "⏰ Надішли бажаний час нагадування у форматі *ГГ:ХХ*\n"
        "Наприклад: `07:30`",
        parse_mode="Markdown",
    )
    await state.set_state(SetTimeState.waiting_for_time)


@router.message(SetTimeState.waiting_for_time)
async def receive_time(message: Message, state: FSMContext) -> None:
    text = message.text.strip() if message.text else ""
    if not re.match(r"^\d{1,2}:\d{2}$", text):
        await message.answer("❌ Невірний формат. Спробуй ще раз: `07:30`", parse_mode="Markdown")
        return

    hour, minute = map(int, text.split(":"))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        await message.answer("❌ Невірний час. Год: 0-23, хвилини: 0-59")
        return

    time_str = f"{hour:02d}:{minute:02d}:00"
    await database.update_user(message.from_user.id, {"notification_time": time_str})
    await state.clear()
    await message.answer(
        f"✅ Нагадування встановлено на *{hour:02d}:{minute:02d}*",
        parse_mode="Markdown",
    )


# ── Free-text entry ───────────────────────────────────────────────────────────

@router.message(lambda m: m.text and not m.text.startswith("/"))
async def handle_text(message: Message) -> None:
    text = message.text.strip()

    # Ignore very short messages
    if len(text) < 10:
        await message.answer(
            "Надто коротко 😅 Опиши детальніше або надішли голосове повідомлення."
        )
        return

    entry_type = _detect_type(text)
    await process_entry(
        message=message,
        bot=message.bot,
        raw_text=text,
        entry_type=entry_type,
        voice_file_id=None,
        transcribed=False,
    )
