# Деплой Dream Journal

## Огляд архітектури

```
GitHub repo
├── bot/          → Railway (бот + FastAPI в одному процесі)
└── mini_app/     → Vercel (React статика)
```

---

## Крок 1 — Supabase

1. Зайди на https://supabase.com → **New project**
2. Запам'ятай: `Project URL` та `service_role key` (Settings → API)
3. SQL Editor → виконай вміст `supabase/migrations/001_initial_schema.sql`

---

## Крок 2 — GitHub

```bash
# Один раз — створи repo на github.com, потім:
git remote add origin https://github.com/ВАШ_НІКНЕЙМ/dream-journal.git
git branch -M main
git push -u origin main
```

---

## Крок 3 — Vercel (Mini App)

1. Зайди на https://vercel.com → **Add New Project**
2. Імпортуй свій GitHub repo
3. Вкажи **Root Directory** = `mini_app`
4. Framework Preset = **Vite**
5. Додай Environment Variable:
   ```
   VITE_API_URL = https://ВАШ_RAILWAY_URL/api
   ```
   _(Railway URL дізнаєшся на кроці 4 — можна повернутись і додати пізніше)_
6. Натисни **Deploy**
7. Збережи URL: `https://dream-journal-xxx.vercel.app`

---

## Крок 4 — Railway (Bot + API)

1. Зайди на https://railway.app → **New Project → Deploy from GitHub**
2. Вибери свій repo
3. Railway знайде `railway.toml` і використає `bot/Dockerfile` автоматично
4. Перейди у **Variables** і додай всі змінні:

| Змінна | Звідки брати |
|--------|-------------|
| `BOT_TOKEN` | @BotFather у Telegram |
| `SUPABASE_URL` | Supabase → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API |
| `GROQ_API_KEY` | https://console.groq.com |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `MINI_APP_URL` | URL з Vercel (крок 3) |

5. Railway автоматично задеплоїть і дасть публічний URL типу `https://dream-journal.up.railway.app`
6. Цей URL встав у Vercel як `VITE_API_URL` (якщо не зробив раніше) і зроби **Redeploy**

---

## Крок 5 — Зареєструй Mini App у @BotFather

```
/newapp
→ вибери свого бота
→ вкажи назву: Dream Journal
→ вкажи URL: https://dream-journal-xxx.vercel.app
```

---

## Готово!

Відтепер у боті з'явиться кнопка **🗂 Журнал** яка відкриває Mini App.

---

## Локальна розробка

```bash
# Бот + API
cd bot
cp .env.example .env    # заповни ключі
pip install -r requirements.txt
python main.py

# Mini App (в іншому терміналі)
cd mini_app
cp .env.example .env    # VITE_API_URL=http://localhost:8000/api
npm install
npm run dev
```

Або через Docker:
```bash
cd bot && cp .env.example .env   # заповни ключі
docker-compose up --build
```
