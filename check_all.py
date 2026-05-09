import json

with open('/Users/Batyr/Documents/exam_screens/questions.json', encoding='utf-8') as f:
    data = json.load(f)

errors = []
warnings = []

for q in data:
    n = q['num']
    
    # Проверка correct
    if q.get('correct') not in [0,1,2,3]:
        errors.append(f"Q{n}: correct={q.get('correct')} вне диапазона 0-3")
    
    # Проверка вариантов
    en_opts = q.get('en_options', [])
    ru_opts = q.get('ru_options', [])
    if len(en_opts) < 2:
        errors.append(f"Q{n}: меньше 2 вариантов EN")
    if len(ru_opts) < 2:
        errors.append(f"Q{n}: меньше 2 вариантов RU")
    if len(en_opts) != len(ru_opts):
        errors.append(f"Q{n}: EN={len(en_opts)} вариантов, RU={len(ru_opts)}")
    
    # correct не выходит за количество вариантов
    if q.get('correct', 0) >= len(en_opts):
        errors.append(f"Q{n}: correct={q.get('correct')} >= вариантов={len(en_opts)}")
    
    # Проверка текстов
    if not q.get('en_q','').strip():
        errors.append(f"Q{n}: пустой en_q")
    if not q.get('ru_q','').strip():
        errors.append(f"Q{n}: пустой ru_q")
    
    # Проверка объяснений
    ru_ex = q.get('ru_explain','').strip()
    en_ex = q.get('en_explain','').strip()
    if not ru_ex:
        errors.append(f"Q{n}: пустой ru_explain")
    elif ru_ex == en_ex:
        warnings.append(f"Q{n}: ru_explain == en_explain (не переведено)")
    
    # Тема
    if not q.get('topic','').strip():
        errors.append(f"Q{n}: нет темы")

print(f"Всего вопросов: {len(data)}")
print(f"Ошибок: {len(errors)}")
print(f"Предупреждений: {len(warnings)}")

if errors:
    print("\nОШИБКИ:")
    for e in errors:
        print(f"  {e}")

if warnings:
    print(f"\nНЕ ПЕРЕВЕДЕНО ({len(warnings)}):")
    for w in warnings[:10]:
        print(f"  {w}")
    if len(warnings) > 10:
        print(f"  ... и ещё {len(warnings)-10}")

if not errors and not warnings:
    print("\nВсе вопросы OK!")
