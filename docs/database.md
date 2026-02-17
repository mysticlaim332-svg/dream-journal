# Database Schema — Dream & Idea Journal

## Структура таблиць

```
users
  ├── id (uuid PK)
  ├── telegram_id (bigint, unique) ← аутентифікація
  ├── username / first_name
  ├── language (uk | en)
  ├── notifications_enabled (bool)
  ├── notification_time (time) ← коли нагадувати
  └── timezone

entries ← головна таблиця
  ├── id (uuid PK)
  ├── user_id → users.id
  ├── type (dream | idea | thought)
  ├── raw_text ← оригінальний текст (або транскрипція голосу)
  ├── voice_file_id ← Telegram file_id аудіо (якщо голосове)
  └── is_analyzed ← флаг: чи вже обробив AI

ai_analysis ← 1-to-1 з entries
  ├── id (uuid PK)
  ├── entry_id → entries.id (unique)
  ├── summary ← 1-3 речення від Claude
  ├── tags (text[]) ← ['#ліс', '#тривога', '#невідоме']
  ├── emotional_tone (positive | neutral | anxious | exciting | sad | mixed)
  ├── key_themes (text[])
  └── raw_response (jsonb) ← повна відповідь Claude для дебагу

entry_connections ← зв'язки між записами (виявлені AI)
  ├── entry_id_a → entries.id
  ├── entry_id_b → entries.id
  ├── connection_type (recurring_theme | similar_emotion | related_idea | same_symbol)
  ├── description ← пояснення зв'язку
  └── similarity_score (0.0 – 1.0)
```

## Налаштування Supabase

1. Створи проект на [supabase.com](https://supabase.com)
2. Перейди в **SQL Editor**
3. Виконай `migrations/001_initial_schema.sql`
4. (Опційно для розробки) Виконай `migrations/002_seed_dev.sql`
   - Заміни `123456789` на свій реальний Telegram ID

## Змінні середовища

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...   # тільки на бекенді бота
```

## RLS (Row Level Security)

Кожен користувач бачить **лише свої** дані. Бот використовує `service_role_key`
і встановлює `app.telegram_id` перед кожним запитом, щоб RLS спрацьовував
коректно.

## Корисні запити

```sql
-- Всі записи користувача, найновіші першими
select e.*, a.summary, a.tags, a.emotional_tone
from entries e
left join ai_analysis a on a.entry_id = e.id
where e.user_id = (select id from users where telegram_id = $1)
order by e.created_at desc;

-- Всі записи за конкретну дату (для календаря Mini App)
select * from entries
where user_id = $1
  and created_at::date = $2::date
order by created_at;

-- Зв'язки для конкретного запису
select ec.*, e.raw_text, a.summary
from entry_connections ec
join entries e on e.id = ec.entry_id_b
join ai_analysis a on a.entry_id = e.id
where ec.entry_id_a = $1
order by ec.similarity_score desc;
```
