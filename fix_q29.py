import json
with open('/Users/Batyr/Documents/exam_screens/questions.json', encoding='utf-8') as f:
    data = json.load(f)
for q in data:
    if q['num'] == 29:
        q['en_q'] = 'A _____________ provides the shortest distance between any two points on the Earth\'s surface.'
        q['ru_q'] = '_____________ обеспечивает кратчайшее расстояние между любыми двумя точками на поверхности Земли.'
        q['en_options'] = ['A) Great circle', 'B) Rhumb line', 'C) Mercator line', 'D) Parallel of latitude']
        q['ru_options'] = ['A) Ортодромия (Great circle)', 'B) Локсодрома (Rhumb line)', 'C) Линия Меркатора', 'D) Параллель широты']
        q['correct'] = 0
        q['en_explain'] = 'A great circle is the shortest distance between two points on the Earth\'s surface. A rhumb line crosses all meridians at the same angle and is easier to navigate but is not the shortest distance. Per American Practical Navigator (Bowditch).'
        q['ru_explain'] = 'Ортодромия (Great circle) — кратчайшее расстояние между двумя точками на поверхности Земли. Локсодрома (Rhumb line) пересекает все меридианы под одним углом, удобна для навигации, но не является кратчайшим путём. Источник: American Practical Navigator (Bowditch).'
        print('Q29 fixed!')
        break
with open('/Users/Batyr/Documents/exam_screens/questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Saved.')
