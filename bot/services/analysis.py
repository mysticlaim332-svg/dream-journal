"""
AI analysis via Claude API.
Analyzes dream/idea text and returns structured insights.
"""
import json
import re
from anthropic import AsyncAnthropic
from config import config
import database

_client = AsyncAnthropic(api_key=config.anthropic_api_key)

SYSTEM_PROMPT = """Ти — асистент для аналізу снів та ідей.
Ти отримуєш запис сну, ідеї або думки і маєш проаналізувати його.

Відповідай ЛИШЕ валідним JSON без жодного додаткового тексту.
Якщо запис українською — аналізуй українською. Якщо англійською — англійською.
"""

ANALYSIS_TEMPLATE = """\
Проаналізуй цей запис і поверни JSON з такою структурою:
{
  "summary": "1-3 речення що описують суть запису",
  "tags": ["#тег1", "#тег2", "#тег3"],
  "emotional_tone": "one of: positive | neutral | anxious | exciting | sad | mixed",
  "key_themes": ["тема1", "тема2"],
  "connections": [
    {
      "entry_id": "<uuid попереднього запису>",
      "connection_type": "one of: recurring_theme | similar_emotion | related_idea | same_symbol",
      "description": "коротке пояснення зв'язку",
      "similarity_score": 0.85
    }
  ]
}

Тип запису: {entry_type}
Текст запису:
{text}

{context_section}
"""

CONTEXT_SECTION = """\
Попередні записи (для пошуку зв'язків):
{context}
"""


def _build_context(recent: list[dict]) -> str:
    if not recent:
        return ""
    lines = []
    for item in recent:
        analysis = item.get("ai_analysis") or {}
        if not analysis:
            continue
        lines.append(
            f"- ID: {item['id']} | {item['type']} | "
            f"Теми: {', '.join(analysis.get('key_themes', []))} | "
            f"Теги: {', '.join(analysis.get('tags', []))}"
        )
    return CONTEXT_SECTION.format(context="\n".join(lines)) if lines else ""


def _parse_response(text: str) -> dict:
    """Extract JSON from Claude response robustly."""
    text = text.strip()
    # strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def analyze_entry(
    entry_id: str,
    user_id: str,
    raw_text: str,
    entry_type: str,
    language: str = "uk",
) -> dict:
    """
    Send entry to Claude for analysis.
    Fetches recent entries for context (recurring theme detection).
    Returns the parsed analysis dict.
    """
    recent = await database.get_recent_analyses(user_id, limit=10)
    # exclude the current entry from context
    recent = [r for r in recent if r["id"] != entry_id]

    context_section = _build_context(recent)
    prompt = ANALYSIS_TEMPLATE.format(
        entry_type=entry_type,
        text=raw_text,
        context_section=context_section,
    )

    message = await _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_response_text = message.content[0].text
    parsed = _parse_response(raw_response_text)

    # Validate and sanitise fields
    summary = parsed.get("summary", "")
    tags = [str(t) for t in parsed.get("tags", [])][:8]
    emotional_tone = parsed.get("emotional_tone", "neutral")
    if emotional_tone not in ("positive", "neutral", "anxious", "exciting", "sad", "mixed"):
        emotional_tone = "neutral"
    key_themes = [str(t) for t in parsed.get("key_themes", [])][:5]
    connections = parsed.get("connections", [])

    # Save analysis to DB
    await database.save_analysis(
        entry_id=entry_id,
        summary=summary,
        tags=tags,
        emotional_tone=emotional_tone,
        key_themes=key_themes,
        raw_response={"text": raw_response_text},
    )

    # Save detected connections
    for conn in connections:
        related_id = conn.get("entry_id")
        # verify this entry_id exists in recent entries
        known_ids = {r["id"] for r in recent}
        if related_id and related_id in known_ids:
            await database.save_connection(
                entry_id_a=entry_id,
                entry_id_b=related_id,
                connection_type=conn.get("connection_type", "related_idea"),
                description=conn.get("description", ""),
                similarity_score=float(conn.get("similarity_score", 0.5)),
            )

    await database.mark_entry_analyzed(entry_id)

    return {
        "summary": summary,
        "tags": tags,
        "emotional_tone": emotional_tone,
        "key_themes": key_themes,
        "connections": connections,
    }


TONE_EMOJI = {
    "positive": "🌟",
    "neutral": "🌙",
    "anxious": "🌀",
    "exciting": "⚡",
    "sad": "🌧",
    "mixed": "🌈",
}

TYPE_LABEL = {
    "dream": "Сон",
    "idea": "Ідея",
    "thought": "Думка",
}


def format_analysis_message(analysis: dict, entry_type: str, transcribed_text: str | None = None) -> str:
    """Format Claude analysis into a readable Telegram message."""
    tone = analysis["emotional_tone"]
    emoji = TONE_EMOJI.get(tone, "🌙")
    label = TYPE_LABEL.get(entry_type, entry_type.capitalize())

    tags_str = " ".join(analysis["tags"]) if analysis["tags"] else "—"
    themes_str = " · ".join(analysis["key_themes"]) if analysis["key_themes"] else "—"

    lines = [
        f"{emoji} *{label} збережено*",
        "",
        f"📝 *Резюме:* {analysis['summary']}",
        "",
        f"🏷 *Теги:* {tags_str}",
        f"🔑 *Теми:* {themes_str}",
        f"💭 *Настрій:* {tone}",
    ]

    if analysis.get("connections"):
        lines.append("")
        lines.append("🔗 *Схожі записи знайдено!*")
        for conn in analysis["connections"][:2]:
            lines.append(f"   └ {conn.get('description', '')}")

    if transcribed_text:
        lines.append("")
        lines.append(f"🎙 _Текст розпізнано з голосового_")

    return "\n".join(lines)
