import anthropic
import time

client = anthropic.Anthropic()

input_file = '/Users/Batyr/Documents/exam_screens/questions_final2.txt'
output_file = '/Users/Batyr/Documents/exam_screens/questions_translated.txt'

content = open(input_file, encoding='utf-8').read()
blocks = [b.strip() for b in content.split('---') if b.strip()]

print(f"Всего вопросов: {len(blocks)}")

results = []

for i, block in enumerate(blocks):
    print(f"Перевожу {i+1}/{len(blocks)}...")
    
    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": f"""Ты помогаешь разрабатывать Telegram-бот @Captain6PackBotRU для подготовки к экзамену USCG Captain's License (6-Pack).

Вот вопрос из теста:

{block}

Сделай следующее:
1. Переведи вопрос на русский язык с морскими терминами (не дословно)
2. Переведи все варианты ответов на русский
3. Напиши объяснение на русском ТОЛЬКО из официальных источников: COLREGS, US Inland Navigation Rules (33 CFR Part 83), NOAA/NGA для карт и погоды
4. Определи тему: sound_signals / lights_shapes / steering_rules / narrow_channels / restricted_visibility / charts / weather / other

ГРАММАТИКА:
- Судно = средний род (оно/его)
- Танкер/корабль = мужской род (он/его)
- Огонь = мужской род (он/его)

Если не уверен в объяснении — пиши ⚠️ вместо объяснения.

Отвечай СТРОГО в этом формате без лишнего текста:
RU_ВОПРОС: ...
RU_A: ...
RU_B: ...
RU_C: ...
RU_D: ...
ТЕМА: ...
ОБЪЯСНЕНИЕ: ..."""
            }]
        )
        
        translation = response.content[0].text.strip()
        results.append(f"{block}\n\n{translation}")
        
    except Exception as e:
        print(f"  Ошибка: {e}")
        results.append(f"{block}\n\n⚠️ ОШИБКА ПЕРЕВОДА")
    
    time.sleep(0.5)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n\n---\n\n'.join(results))

print(f"\nГотово! Файл: {output_file}")
