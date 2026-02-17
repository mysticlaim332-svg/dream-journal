"""
Voice message handler — the core flow:
  voice → transcribe → detect type → analyze → respond
"""
import logging
from aiogram import Router, Bot
from aiogram.types import Message
import database
from services.transcription import transcribe
from services.analysis import analyze_entry, format_analysis_message
import keyboards

logger = logging.getLogger(__name__)
router = Router()


async def _process_entry(
    message: Message,
    bot: Bot,
    raw_text: str,
    entry_type: str,
    voice_file_id: str | None = None,
    transcribed: bool = False,
) -> None:
    """Shared logic: save entry → analyze → reply."""
    user = await database.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    entry = await database.create_entry(
        user_id=user["id"],
        raw_text=raw_text,
        entry_type=entry_type,
        voice_file_id=voice_file_id,
    )

    # Show "analyzing..." indicator
    thinking_msg = await message.answer("🔍 _Аналізую..._", parse_mode="Markdown")

    try:
        analysis = await analyze_entry(
            entry_id=entry["id"],
            user_id=user["id"],
            raw_text=raw_text,
            entry_type=entry_type,
            language=user.get("language", "uk"),
        )
    except Exception as e:
        logger.error(f"Analysis failed for entry {entry['id']}: {e}")
        await thinking_msg.delete()
        await message.answer(
            "✅ Запис збережено, але аналіз не вдався. Спробуємо пізніше.",
        )
        return

    await thinking_msg.delete()

    reply_text = format_analysis_message(
        analysis=analysis,
        entry_type=entry_type,
        transcribed_text=raw_text if transcribed else None,
    )
    await message.answer(reply_text, parse_mode="Markdown")


@router.message(lambda m: m.voice is not None)
async def handle_voice(message: Message, bot: Bot) -> None:
    user = await database.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    language = user.get("language", "uk")

    # Show transcribing indicator
    status_msg = await message.answer("🎙 _Розпізнаю голос..._", parse_mode="Markdown")

    try:
        text = await transcribe(bot, message.voice.file_id, language=language)
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        await status_msg.delete()
        await message.answer(
            "❌ Не вдалося розпізнати голос. Спробуй ще раз або напиши текстом."
        )
        return

    await status_msg.delete()

    if not text.strip():
        await message.answer("⚠️ Голосове повідомлення порожнє. Спробуй ще раз.")
        return

    # Detect entry type from context (default to 'dream' for morning hours)
    entry_type = _detect_type(text)

    await _process_entry(
        message=message,
        bot=bot,
        raw_text=text,
        entry_type=entry_type,
        voice_file_id=message.voice.file_id,
        transcribed=True,
    )


@router.message(lambda m: m.audio is not None)
async def handle_audio(message: Message, bot: Bot) -> None:
    """Handle regular audio files the same as voice messages."""
    await handle_voice.__wrapped__(message, bot) if hasattr(handle_voice, "__wrapped__") else None
    # redirect: treat audio as voice
    message.voice = message.audio
    await handle_voice(message, bot)


def _detect_type(text: str) -> str:
    """
    Heuristic: guess entry type from text content.
    Claude will refine the summary, but type helps with categorization.
    """
    text_lower = text.lower()
    dream_keywords = ["сни", "снився", "снилося", "снив", "сон", "уві сні", "прокинув", "dreamed", "dream", "woke up"]
    idea_keywords = ["ідея", "думка", "придумав", "треба зробити", "можна", "idea", "thought of"]

    if any(kw in text_lower for kw in dream_keywords):
        return "dream"
    if any(kw in text_lower for kw in idea_keywords):
        return "idea"
    return "thought"


# Export the shared processor for use by text handler
process_entry = _process_entry
