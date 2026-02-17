-- ============================================================
-- Dev seed data — run only in development
-- ============================================================

-- Disable RLS for seeding
set local session_replication_role = replica;

-- Test user (your Telegram ID — replace before running)
insert into users (telegram_id, username, first_name, language, timezone)
values (123456789, 'dev_user', 'Dev', 'uk', 'Europe/Kyiv');

-- Sample entries
with u as (select id from users where telegram_id = 123456789)
insert into entries (user_id, type, raw_text, is_analyzed)
values
    ((select id from u), 'dream',
     'Мені снилось що я йшов через темний ліс і знайшов стару хатину. Всередині горів вогонь і хтось чекав на мене, але я не бачив обличчя. Відчував тривогу але водночас цікавість.',
     false),
    ((select id from u), 'idea',
     'Ідея: зробити додаток який допомагає людям фіксувати сни одразу після пробудження через голосове повідомлення. AI аналізує і знаходить патерни.',
     false),
    ((select id from u), 'thought',
     'Думаю про те що потрібно більше часу на відпочинок. Робота займає занадто багато ментальних ресурсів.',
     false);

-- Re-enable RLS
set local session_replication_role = default;
