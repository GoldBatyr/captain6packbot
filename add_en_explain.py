import anthropic
import time

client = anthropic.Anthropic()

input_file = '/Users/Batyr/Documents/exam_screens/questions_translated.txt'

content = open(input_file, encoding='utf-8').read()
blocks = [b.strip() for b in content.split('---') if b.strip()]

print(f'Всего вопросов: {len(blocks)}')

for i, block in enumerate(blocks):
    if 'EN_EXPLAIN:' in block:
        continue
    print(f'Обрабатываю {i+1}/{len(blocks)}...')
    try:
        vopros = ''
        for line in block.split('\n'):
            if line.startswith('ВОПРОС:'):
                vopros = line
                break
        response = client.messages.create(
            model='claude-opus-4-5',
            max_tokens=400,
            messages=[{'role': 'user', 'content': f'''Write a short English explanation (2-3 sentences) for this USCG Captain 6-Pack exam question. Use proper American maritime terminology. Reference the specific Rule (COLREGS or US Inland Rules). No preamble, just the explanation.

{vopros}
Correct answer is marked as ОТВЕТ in the text below.

{block[:300]}'''}])
        en_explain = response.content[0].text.strip()
        blocks[i] = block + f'\n\nEN_EXPLAIN: {en_explain}'
    except Exception as e:
        print(f'  Ошибка: {e}')
    time.sleep(0.3)

with open(input_file, 'w', encoding='utf-8') as f:
    f.write('\n\n---\n\n'.join(blocks))
print('Готово!')
