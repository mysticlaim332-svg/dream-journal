"""
FastAPI backend for the Telegram Mini App.
Validates Telegram initData, then serves entries from Supabase.

Run alongside the bot:
    uvicorn api:app --host 0.0.0.0 --port 8000
"""
import hashlib
import hmac
import json
import logging
from datetime import datetime
from urllib.parse import parse_qs, unquote

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware

import database
from config import config

logger = logging.getLogger(__name__)
app = FastAPI(title="Dream Journal API", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Telegram Mini Apps run from tg:// or https://
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ── Auth ──────────────────────────────────────────────────────────────────────

def _validate_init_data(init_data: str) -> dict:
    """
    Verify Telegram WebApp initData using HMAC-SHA256.
    Returns parsed user dict or raises 401.
    """
    parsed = parse_qs(unquote(init_data))
    hash_value = parsed.pop("hash", [None])[0]
    if not hash_value:
        raise HTTPException(status_code=401, detail="Missing hash")

    # Build data-check-string: sorted key=value pairs joined by \n
    data_check_string = "\n".join(
        f"{k}={v[0]}" for k, v in sorted(parsed.items())
    )

    # HMAC-SHA256(secret_key, data_check_string)
    # secret_key = HMAC-SHA256("WebAppData", bot_token)
    secret_key = hmac.new(
        b"WebAppData",
        config.bot_token.encode(),
        hashlib.sha256,
    ).digest()

    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, hash_value):
        raise HTTPException(status_code=401, detail="Invalid initData")

    user_raw = parsed.get("user", [None])[0]
    if not user_raw:
        raise HTTPException(status_code=401, detail="No user in initData")

    return json.loads(user_raw)


async def _get_user_from_header(x_init_data: str | None) -> dict:
    if not x_init_data:
        raise HTTPException(status_code=401, detail="Missing X-Init-Data header")
    tg_user = _validate_init_data(x_init_data)
    user = await database.get_or_create_user(
        telegram_id=tg_user["id"],
        username=tg_user.get("username"),
        first_name=tg_user.get("first_name"),
    )
    return user


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/entries")
async def get_entries(
    month: str = Query(None, description="YYYY-MM format, e.g. 2024-01"),
    x_init_data: str | None = Header(None),
):
    """
    Returns entries for the given month (or all if omitted).
    Groups by date for the calendar view.
    """
    user = await _get_user_from_header(x_init_data)
    db = database.get_db()

    query = (
        db.table("entries")
        .select("id, type, raw_text, voice_file_id, is_analyzed, created_at, ai_analysis(summary, tags, emotional_tone, key_themes)")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
    )

    if month:
        try:
            dt = datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise HTTPException(status_code=400, detail="Month must be YYYY-MM")
        # filter by month using gte/lte
        start = dt.strftime("%Y-%m-01T00:00:00")
        # last day of month
        if dt.month == 12:
            end = f"{dt.year + 1}-01-01T00:00:00"
        else:
            end = f"{dt.year}-{dt.month + 1:02d}-01T00:00:00"
        query = query.gte("created_at", start).lt("created_at", end)

    result = query.execute()
    entries = result.data or []

    # Group by date for calendar
    by_date: dict[str, list] = {}
    for entry in entries:
        date = entry["created_at"][:10]
        by_date.setdefault(date, []).append(entry)

    return {"entries": entries, "by_date": by_date}


@app.get("/api/entries/{entry_id}")
async def get_entry(entry_id: str, x_init_data: str | None = Header(None)):
    user = await _get_user_from_header(x_init_data)
    db = database.get_db()

    result = (
        db.table("entries")
        .select("*, ai_analysis(*), entry_connections!entry_id_a(*, entries!entry_id_b(id, type, raw_text, created_at, ai_analysis(summary)))")
        .eq("id", entry_id)
        .eq("user_id", user["id"])
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Entry not found")
    return result.data


@app.get("/api/stats")
async def get_stats(x_init_data: str | None = Header(None)):
    """Returns aggregated stats: top tags, mood distribution, entries per month."""
    user = await _get_user_from_header(x_init_data)
    db = database.get_db()

    # Get all analyses for this user
    result = (
        db.table("entries")
        .select("type, created_at, ai_analysis(tags, emotional_tone, key_themes)")
        .eq("user_id", user["id"])
        .eq("is_analyzed", True)
        .order("created_at", desc=True)
        .limit(200)
        .execute()
    )
    entries = result.data or []

    # Aggregate
    tag_counts: dict[str, int] = {}
    mood_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    monthly: dict[str, int] = {}

    for entry in entries:
        # type
        type_counts[entry["type"]] = type_counts.get(entry["type"], 0) + 1
        # month
        month = entry["created_at"][:7]
        monthly[month] = monthly.get(month, 0) + 1

        analysis = entry.get("ai_analysis") or {}
        if not analysis:
            continue
        # tags
        for tag in analysis.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        # mood
        tone = analysis.get("emotional_tone", "neutral")
        mood_counts[tone] = mood_counts.get(tone, 0) + 1

    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    return {
        "total_entries": len(entries),
        "type_counts": type_counts,
        "mood_counts": mood_counts,
        "top_tags": [{"tag": t, "count": c} for t, c in top_tags],
        "monthly": dict(sorted(monthly.items())),
    }
