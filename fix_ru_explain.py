import json
import os
import time
import urllib.request
import urllib.error

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
JSON_PATH = "/Users/Batyr/Documents/exam_screens/questions.json"

with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

bad = [q for q in data if not q.get("ru_explain") or q["ru_explain"].strip() in ["", "⚠️"]]
print(f"Вопросов без ru_explain: {len(bad)}")

def translate_explain(en_explain, en_q):
    prompt = f"""Переведи это объяснение к экзаменационному вопросу USCG Captain 6-Pack на русский язык.
Используй правильные морские термины. Не добавляй ничего лишнего — только перевод.
Вопрос: {en_q}
Объяснение EN: {en_explain}
Дай только русский текст объяснения, без вступлений."""

    body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 300,
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
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        return result["content"][0]["text"].strip()

for i, q in enumerate(bad):
    print(f"[{i+1}/{len(bad)}] Q{q['num']}...", end=" ", flush=True)
    try:
        ru = translate_explain(q["en_explain"], q["en_q"])
        q["ru_explain"] = ru
        print("OK")
    except Exception as e:
        print(f"ОШИБКА: {e}")
        q["ru_explain"] = q["en_explain"]
    time.sleep(0.5)

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nГотово! Сохранено в {JSON_PATH}")
