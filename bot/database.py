from supabase import create_client, Client
from config import config
from typing import Optional
import uuid

_client: Optional[Client] = None


def get_db() -> Client:
    global _client
    if _client is None:
        _client = create_client(config.supabase_url, config.supabase_key)
    return _client


# ── Users ────────────────────────────────────────────────────────────────────

async def get_or_create_user(telegram_id: int, username: str | None, first_name: str | None) -> dict:
    db = get_db()
    result = db.table("users").select("*").eq("telegram_id", telegram_id).maybe_single().execute()

    if result.data:
        return result.data

    new_user = {
        "telegram_id": telegram_id,
        "username": username,
        "first_name": first_name,
    }
    result = db.table("users").insert(new_user).select().single().execute()
    return result.data


async def get_user(telegram_id: int) -> dict | None:
    db = get_db()
    result = db.table("users").select("*").eq("telegram_id", telegram_id).maybe_single().execute()
    return result.data


async def update_user(telegram_id: int, data: dict) -> dict:
    db = get_db()
    result = (
        db.table("users")
        .update(data)
        .eq("telegram_id", telegram_id)
        .select()
        .single()
        .execute()
    )
    return result.data


# ── Entries ──────────────────────────────────────────────────────────────────

async def create_entry(
    user_id: str,
    raw_text: str,
    entry_type: str = "dream",
    voice_file_id: str | None = None,
) -> dict:
    db = get_db()
    data = {
        "user_id": user_id,
        "type": entry_type,
        "raw_text": raw_text,
        "voice_file_id": voice_file_id,
        "is_analyzed": False,
    }
    result = db.table("entries").insert(data).select().single().execute()
    return result.data


async def mark_entry_analyzed(entry_id: str) -> None:
    db = get_db()
    db.table("entries").update({"is_analyzed": True}).eq("id", entry_id).execute()


async def get_user_entries(user_id: str, limit: int = 50) -> list[dict]:
    db = get_db()
    result = (
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
    db = get_db()
    result = (
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
    db = get_db()
    data = {
        "entry_id": entry_id,
        "summary": summary,
        "tags": tags,
        "emotional_tone": emotional_tone,
        "key_themes": key_themes,
        "raw_response": raw_response,
    }
    result = db.table("ai_analysis").insert(data).select().single().execute()
    return result.data


# ── Connections ───────────────────────────────────────────────────────────────

async def save_connection(
    entry_id_a: str,
    entry_id_b: str,
    connection_type: str,
    description: str,
    similarity_score: float,
) -> None:
    db = get_db()
    # entry_id_a is always the newer entry
    db.table("entry_connections").upsert({
        "entry_id_a": entry_id_a,
        "entry_id_b": entry_id_b,
        "connection_type": connection_type,
        "description": description,
        "similarity_score": similarity_score,
    }, on_conflict="entry_id_a,entry_id_b").execute()


async def get_users_with_notifications() -> list[dict]:
    """Return all users who have notifications enabled."""
    db = get_db()
    result = (
        db.table("users")
        .select("telegram_id, notification_time, timezone")
        .eq("notifications_enabled", True)
        .execute()
    )
    return result.data or []
