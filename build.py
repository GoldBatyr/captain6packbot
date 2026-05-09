import re

content = open('/Users/Batyr/Documents/exam_screens/questions_translated.txt', encoding='utf-8').read()
blocks = [b.strip() for b in content.split('---') if b.strip()]

def get_field(block, field):
    for line in block.split('\n'):
        if line.startswith(field + ':'):
            return line[len(field)+1:].strip()
    return ''

def get_multiline(block, field):
    lines = block.split('\n')
    result = []
    found = False
    for line in lines:
        if line.startswith(field + ':'):
            result.append(line[len(field)+1:].strip())
            found = True
        elif found and line.startswith(('ВОПРОС:', 'A:', 'B:', 'C:', 'D:', 'ОТВЕТ:', 'КАРТИНКА:', 'RU_ВОПРОС:', 'RU_A:', 'RU_B:', 'RU_C:', 'RU_D:', 'ТЕМА:', 'ОБЪЯСНЕНИЕ:', 'EN_EXPLAIN:', 'Вопрос ')):
            break
        elif found:
            result.append(line)
    return ' '.join(result).strip()

def clean(s):
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace("'", "\\'")
    return s

answer_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

output = []
output.append('NEW_QUESTIONS = [')

for i, block in enumerate(blocks):
    en_q = clean(get_field(block, 'ВОПРОС'))
    en_a = clean(get_field(block, 'A'))
    en_b = clean(get_field(block, 'B'))
    en_c = clean(get_field(block, 'C'))
    en_d = clean(get_field(block, 'D'))
    answer_letter = get_field(block, 'ОТВЕТ').strip().upper()
    correct = answer_map.get(answer_letter, 0)
    ru_q = clean(get_field(block, 'RU_ВОПРОС'))
    ru_a = clean(get_field(block, 'RU_A'))
    ru_b = clean(get_field(block, 'RU_B'))
    ru_c = clean(get_field(block, 'RU_C'))
    ru_d = clean(get_field(block, 'RU_D'))
    topic = get_field(block, 'ТЕМА').lower().replace(' ', '_')
    ru_explain = clean(get_multiline(block, 'ОБЪЯСНЕНИЕ'))
    en_explain = clean(get_multiline(block, 'EN_EXPLAIN'))

    output.append(f'    {{\n        "num": {i+1},\n        "topic": "{topic}",\n        "en_q": "{en_q}",\n        "ru_q": "{ru_q}",\n        "en_options": ["A) {en_a}", "B) {en_b}", "C) {en_c}", "D) {en_d}"],\n        "ru_options": ["A) {ru_a}", "B) {ru_b}", "C) {ru_c}", "D) {ru_d}"],\n        "correct": {correct},\n        "en_explain": "{en_explain}",\n        "ru_explain": "{ru_explain}",\n        "image": None,\n    }},')

output.append(']')

result = '\n'.join(output)
open('/Users/Batyr/Documents/exam_screens/new_questions.py', 'w', encoding='utf-8').write(result)
print(f'Готово! Собрано вопросов: {len(blocks)}')
