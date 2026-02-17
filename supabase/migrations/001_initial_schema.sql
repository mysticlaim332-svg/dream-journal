-- ============================================================
-- Dream & Idea Journal — Initial Schema
-- ============================================================

-- Enable UUID generation
create extension if not exists "pgcrypto";

-- ============================================================
-- ENUM TYPES
-- ============================================================

create type entry_type as enum ('dream', 'idea', 'thought');
create type emotional_tone as enum ('positive', 'neutral', 'anxious', 'exciting', 'sad', 'mixed');
create type connection_type as enum ('recurring_theme', 'similar_emotion', 'related_idea', 'same_symbol');

-- ============================================================
-- TABLE: users
-- Telegram users, auth via Telegram ID
-- ============================================================

create table users (
    id                    uuid primary key default gen_random_uuid(),
    telegram_id           bigint unique not null,
    username              text,
    first_name            text,
    language              text not null default 'uk' check (language in ('uk', 'en')),
    notifications_enabled boolean not null default true,
    notification_time     time not null default '08:00:00',
    timezone              text not null default 'Europe/Kyiv',
    created_at            timestamptz not null default now(),
    updated_at            timestamptz not null default now()
);

-- ============================================================
-- TABLE: entries
-- Main table for dreams, ideas, and thoughts
-- ============================================================

create table entries (
    id             uuid primary key default gen_random_uuid(),
    user_id        uuid not null references users(id) on delete cascade,
    type           entry_type not null default 'dream',
    raw_text       text not null,
    voice_file_id  text,                    -- Telegram file_id for original audio
    is_analyzed    boolean not null default false,
    created_at     timestamptz not null default now(),
    updated_at     timestamptz not null default now()
);

-- ============================================================
-- TABLE: ai_analysis
-- AI-generated analysis for each entry (1-to-1 with entries)
-- ============================================================

create table ai_analysis (
    id              uuid primary key default gen_random_uuid(),
    entry_id        uuid unique not null references entries(id) on delete cascade,
    summary         text not null,           -- 1-3 sentence summary
    tags            text[] not null default '{}',
    emotional_tone  emotional_tone not null default 'neutral',
    key_themes      text[] not null default '{}',
    raw_response    jsonb,                   -- full Claude response for debugging
    created_at      timestamptz not null default now()
);

-- ============================================================
-- TABLE: entry_connections
-- AI-detected links between entries (recurring symbols, themes)
-- ============================================================

create table entry_connections (
    id               uuid primary key default gen_random_uuid(),
    entry_id_a       uuid not null references entries(id) on delete cascade,
    entry_id_b       uuid not null references entries(id) on delete cascade,
    connection_type  connection_type not null,
    description      text,                  -- human-readable reason for connection
    similarity_score float check (similarity_score between 0 and 1),
    created_at       timestamptz not null default now(),
    -- prevent duplicate pairs
    unique (entry_id_a, entry_id_b)
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Fast lookup of all entries for a user, newest first
create index idx_entries_user_created on entries(user_id, created_at desc);

-- Fast lookup of entries by type
create index idx_entries_user_type on entries(user_id, type);

-- Fast lookup of unanalyzed entries (for retry queue)
create index idx_entries_unanalyzed on entries(user_id) where is_analyzed = false;

-- Fast lookup of connections for an entry
create index idx_connections_entry_a on entry_connections(entry_id_a);
create index idx_connections_entry_b on entry_connections(entry_id_b);

-- ============================================================
-- FUNCTIONS & TRIGGERS
-- Auto-update updated_at timestamp
-- ============================================================

create or replace function set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger trg_users_updated_at
    before update on users
    for each row execute function set_updated_at();

create trigger trg_entries_updated_at
    before update on entries
    for each row execute function set_updated_at();

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- Each user sees only their own data
-- ============================================================

alter table users enable row level security;
alter table entries enable row level security;
alter table ai_analysis enable row level security;
alter table entry_connections enable row level security;

-- Users can only read/update their own profile
create policy "users: own row only"
    on users for all
    using (telegram_id = (current_setting('app.telegram_id', true))::bigint);

-- Users can only access their own entries
create policy "entries: own only"
    on entries for all
    using (user_id = (
        select id from users
        where telegram_id = (current_setting('app.telegram_id', true))::bigint
    ));

-- Users can only access analysis of their own entries
create policy "ai_analysis: own only"
    on ai_analysis for all
    using (entry_id in (
        select e.id from entries e
        join users u on u.id = e.user_id
        where u.telegram_id = (current_setting('app.telegram_id', true))::bigint
    ));

-- Users can only access connections of their own entries
create policy "entry_connections: own only"
    on entry_connections for all
    using (entry_id_a in (
        select e.id from entries e
        join users u on u.id = e.user_id
        where u.telegram_id = (current_setting('app.telegram_id', true))::bigint
    ));
