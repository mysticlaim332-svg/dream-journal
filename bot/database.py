from supabase import acreate_client, AsyncClient
from config import config
from typing import Optional

_client: Optional[AsyncClient] = None


async def get_db() -> AsyncClient:
    global _client
    if _client is None:
        _client = await acreate_client(config.supabase_url.strip(), config.supabase_key.strip())
    return _client


def _first(result) -> dict | None:
    """Safely get first row from a supabase result."""
    if result and result.data:
        return result.data[0] if isinstance(result.data, list) else result.data
    return None


# ── Users ────────────────────────────────────────────────────────────────────

async def get_or_create_user(telegram_id: int, username: str | None, first_name: str | None) -> dict:
    db = await get_db()
    result = await db.table("users").select("*").eq("telegram_id", telegram_id).limit(1).execute()
    existing = _first(result)
    if existing:
        return existing

    new_user = {
        "telegram_id": telegram_id,
        "username": username,
        "first_name": first_name,
    }
    result = await db.table("users").insert(new_user).execute()
    return _first(result)


async def get_user(telegram_id: int) -> dict | None:
    db = await get_db()
    result = await db.table("users").select("*").eq("telegram_id", telegram_id).limit(1).execute()
    return _first(result)


async def update_user(telegram_id: int, data: dict) -> dict:
    db = await get_db()
    result = await db.table("users").update(data).eq("telegram_id", telegram_id).execute()
    return _first(result)


# ── Entries ──────────────────────────────────────────────────────────────────

async def create_entry(
    user_id: str,
    raw_text: str,
    entry_type: str = "dream",
    voice_file_id: str | None = None,
) -> dict:
    db = await get_db()
    data = {
        "user_id": user_id,
        "type": entry_type,
        "raw_text": raw_text,
        "voice_file_id": voice_file_id,
        "is_analyzed": False,
    }
    result = await db.table("entries").insert(data).execute()
    return _first(result)


async def mark_entry_analyzed(entry_id: str) -> None:
    db = await get_db()
    await db.table("entries").update({"is_analyzed": True}).eq("id", entry_id).execute()


async def get_user_entries(user_id: str, limit: int = 50) -> list[dict]:
    db = await get_db()
    result = await (
        db.table("entries")
        .select("*, ai_analysis(*)")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


async def get_recent_analyses(user_id: str, limit: int = 10) -> list[dict]:
    """Return recent AI analyses for the user — used to detect recurring themes."""
    db = await get_db()
    result = await (
        db.table("entries")
        .select("id, type, created_at, ai_analysis(summary, tags, key_themes, emotional_tone)")
        .eq("user_id", user_id)
        .eq("is_analyzed", True)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


# ── AI Analysis ──────────────────────────────────────────────────────────────

async def save_analysis(
    entry_id: str,
    summary: str,
    tags: list[str],
    emotional_tone: str,
    key_themes: list[str],
    raw_response: dict | None = None,
) -> dict:
    db = await get_db()
    data = {
        "entry_id": entry_id,
        "summary": summary,
        "tags": tags,
        "emotional_tone": emotional_tone,
        "key_themes": key_themes,
        "raw_response": raw_response,
    }
    result = await db.table("ai_analysis").insert(data).execute()
    return _first(result)


# ── Connections ───────────────────────────────────────────────────────────────

async def save_connection(
    entry_id_a: str,
    entry_id_b: str,
    connection_type: str,
    description: str,
    similarity_score: float,
) -> None:
    db = await get_db()
    await db.table("entry_connections").upsert({
        "entry_id_a": entry_id_a,
        "entry_id_b": entry_id_b,
        "connection_type": connection_type,
        "description": description,
        "similarity_score": similarity_score,
    }, on_conflict="entry_id_a,entry_id_b").execute()


async def get_user_connections(user_id: str, limit: int = 50) -> list[dict]:
    """Return AI-detected connections between user's entries."""
    db = await get_db()
    entry_result = await db.table("entries").select("id").eq("user_id", user_id).execute()
    entry_ids = [e["id"] for e in (entry_result.data or [])]
    if not entry_ids:
        return []
    result = await (
        db.table("entry_connections")
        .select("entry_id_a, entry_id_b, connection_type, description, similarity_score")
        .in_("entry_id_a", entry_ids)
        .order("similarity_score", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


async def get_users_with_notifications() -> list[dict]:
    """Return all users who have notifications enabled."""
    db = await get_db()
    result = await (
        db.table("users")
        .select("telegram_id, notification_time, timezone")
        .eq("notifications_enabled", True)
        .execute()
    )
    return result.data or []
