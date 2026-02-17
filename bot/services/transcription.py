"""
Voice → Text via Groq Whisper API.
Groq has a generous free tier and is significantly faster than OpenAI Whisper.
"""
import aiohttp
import aiofiles
import os
import tempfile
from groq import Groq
from config import config

_client = Groq(api_key=config.groq_api_key)


async def download_voice(bot, file_id: str) -> str:
    """Download Telegram voice file and return local temp path."""
    file = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{config.bot_token}/{file.file_path}"

    suffix = os.path.splitext(file.file_path)[1] or ".ogg"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            resp.raise_for_status()
            async with aiofiles.open(tmp.name, "wb") as f:
                await f.write(await resp.read())

    return tmp.name


async def transcribe(bot, file_id: str, language: str = "uk") -> str:
    """
    Download voice message and transcribe it.
    Returns the transcribed text.
    """
    local_path = await download_voice(bot, file_id)

    try:
        # Groq Whisper supports Ukrainian (uk) and English (en)
        lang = language if language in ("uk", "en") else "uk"

        with open(local_path, "rb") as audio_file:
            transcription = _client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=lang,
                response_format="text",
            )
        return transcription.strip()
    finally:
        os.unlink(local_path)
