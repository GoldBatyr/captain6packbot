import anthropic
import time

client = anthropic.Anthropic()

input_file = '/Users/Batyr/Documents/exam_screens/questions_translated.txt'

content = open(input_file, encoding='utf-8').read()
blocks = [b.strip() for b in content.split('---') if b.strip()]

print(f'Всего блоков: {len(blocks)}')
errors = [(i, b) for i, b in enumerate(blocks) if 'ОШИБКА ПЕРЕВОДА' in b]
print(f'Нужно допереводить: {len(errors)}')

for idx, (i, block) in enumerate(errors):
    print(f'Перевожу {idx+1}/{len(errors)}...')
    original = block.split('ОШИБКА ПЕРЕВОДА')[0].strip()
    try:
        response = client.messages.create(
            model='claude-opus-4-5',
            max_tokens=1500,
            messages=[{'role': 'user', 'content': f'Переведи вопрос теста USCG Captain 6-Pack на русский с морскими терминами.\n\n{original}\n\nФормат:\nRU_ВОПРОС: ...\nRU_A: ...\nRU_B: ...\nRU_C: ...\nRU_D: ...\nТЕМА: ...\nОБЪЯСНЕНИЕ: ...'}])
        blocks[i] = f'{original}\n\n{response.content[0].text.strip()}'
    except Exception as e:
        print(f'  Ошибка: {e}')
    time.sleep(0.5)

with open(input_file, 'w', encoding='utf-8') as f:
    f.write('\n\n---\n\n'.join(blocks))
print('Готово!')
