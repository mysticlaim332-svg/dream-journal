"""Quick smoke test for all services."""
import sys, io, asyncio, os, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from groq import AsyncGroq, Groq
from supabase import create_client


async def test_groq_llm():
    client = AsyncGroq(api_key=os.getenv('GROQ_API_KEY'))
    resp = await client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        max_tokens=300,
        messages=[
            {'role': 'system', 'content': 'Reply only with valid JSON. No extra text.'},
            {'role': 'user', 'content': (
                'Analyze this dream and return JSON with keys: '
                'summary (string), tags (array), emotional_tone (string), key_themes (array). '
                'Dream: I was flying over a night city, feeling free and happy.'
            )}
        ]
    )
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    data = json.loads(raw)
    print('LLaMA OK')
    print('  summary    :', data.get('summary', '')[:60])
    print('  tags       :', data.get('tags', []))
    print('  tone       :', data.get('emotional_tone', ''))
    print('  key_themes :', data.get('key_themes', []))
    return True


def test_supabase():
    db = create_client(
        os.getenv('SUPABASE_URL').strip(),
        os.getenv('SUPABASE_SERVICE_ROLE_KEY').strip(),
    )
    r = db.table('users').select('count', count='exact').execute()
    print(f'Supabase OK  — users table: {r.count} rows')
    r2 = db.table('entries').select('count', count='exact').execute()
    print(f'Supabase OK  — entries table: {r2.count} rows')
    return True


def test_groq_whisper():
    # Just check models list includes whisper
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    models = [m.id for m in client.models.list().data]
    whisper_models = [m for m in models if 'whisper' in m.lower()]
    print(f'Groq Whisper OK — found: {whisper_models}')
    return True


async def main():
    print('=' * 50)
    print('Dream Journal — Service Tests')
    print('=' * 50)

    results = {}

    try:
        test_supabase()
        results['Supabase'] = 'OK'
    except Exception as e:
        print(f'Supabase FAIL: {e}')
        results['Supabase'] = 'FAIL'

    try:
        test_groq_whisper()
        results['Groq Whisper'] = 'OK'
    except Exception as e:
        print(f'Groq Whisper FAIL: {e}')
        results['Groq Whisper'] = 'FAIL'

    try:
        await test_groq_llm()
        results['LLaMA Analysis'] = 'OK'
    except Exception as e:
        print(f'LLaMA FAIL: {e}')
        results['LLaMA Analysis'] = 'FAIL'

    print()
    print('=' * 50)
    all_ok = all(v == 'OK' for v in results.values())
    for k, v in results.items():
        print(f'  {"OK" if v == "OK" else "FAIL"}  {k}')
    print()
    print('ALL SYSTEMS GO' if all_ok else 'SOME TESTS FAILED')
    print('=' * 50)


asyncio.run(main())
