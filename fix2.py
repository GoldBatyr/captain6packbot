import json, os, time, urllib.request

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PATH = "/Users/Batyr/Documents/exam_screens/questions.json"

with open(PATH, encoding="utf-8") as f:
    data = json.load(f)

bad = [q for q in data if q.get("ru_explain","") == q.get("en_explain","")]
print(f"To translate: {len(bad)}")

for i, q in enumerate(bad):
    print(f"[{i+1}/{len(bad)}] Q{q['num']}...", end=" ", flush=True)
    try:
        body = json.dumps({"model":"claude-haiku-4-5-20251001","max_tokens":400,"messages":[{"role":"user","content":"Translate to Russian, maritime terms only, no preamble:\n\n"+q["en_explain"]}]}).encode()
        req = urllib.request.Request("https://api.anthropic.com/v1/messages",data=body,headers={"Content-Type":"application/json","x-api-key":API_KEY,"anthropic-version":"2023-06-01"})
        with urllib.request.urlopen(req,timeout=30) as r:
            q["ru_explain"] = json.loads(r.read())["content"][0]["text"].strip()
        print("OK")
    except Exception as e:
        print(f"ERR:{e}")
    time.sleep(0.2)

with open(PATH,"w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)
print("Done!")
