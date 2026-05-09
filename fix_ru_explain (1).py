import json
import os
import time
import urllib.request

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
JSON_PATH = "/Users/Batyr/Documents/exam_screens/questions.json"

with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

def needs_translation(q):
    ru = str(q.get("ru_explain", "")).strip()
    en = str(q.get("en_explain", "")).strip()
    if not ru or ru in ["⚠️", ""]:
        return True
    if ru == en:
        return True
    return False

bad = [q for q in data if needs_translation(q)]
print(f"Вопросов для перевода: {len(bad)}")

def translate(en_explain, en_q):
    prompt = f"Переведи объяснение к экзаменационному вопросу USCG на русский язык. Используй правильные морские термины. Только перевод без вступлений.\n\nВопрос: {en_q}\n\nОбъяснение: {en_explain}"
    body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 400,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
        return result["content"][0]["text"].strip()

for i, q in enumerate(bad):
    print(f"[{i+1}/{len(bad)}] Q{q['num']}...", end=" ", flush=True)
    try:
        en = str(q.get("en_explain", "")).strip()
        if not en:
            print("ПРОПУСК (нет en_explain)")
            continue
        ru = translate(en, str(q.get("en_q", "")))
        q["ru_explain"] = ru
        print("OK")
    except Exception as e:
        print(f"ОШИБКА: {e}")
    time.sleep(0.3)

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nГотово! Сохранено.")
