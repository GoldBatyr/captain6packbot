import json

with open('/Users/Batyr/Documents/exam_screens/questions.json', encoding='utf-8') as f:
    data = json.load(f)

bad_en = [q['num'] for q in data if not q.get('en_explain') or str(q.get('en_explain', '')).strip() == '']
bad_ru = [q['num'] for q in data if not q.get('ru_explain') or str(q.get('ru_explain', '')).strip() in ['', '⚠️']]

print(f'Без en_explain: {len(bad_en)} — {bad_en[:10]}')
print(f'Без ru_explain: {len(bad_ru)} — {bad_ru[:10]}')
