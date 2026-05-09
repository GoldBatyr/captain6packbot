import anthropic
import base64
import json
import os
from pathlib import Path
from PIL import Image
import io

client = anthropic.Anthropic()

photos_dir = Path.home() / "Documents" / "exam_screens" / "photos"
output_file = Path.home() / "Documents" / "exam_screens" / "questions.txt"

image_files = sorted([f for f in photos_dir.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']])

print(f"Найдено фото: {len(image_files)}")

results = []
question_num = 131

for i, img_path in enumerate(image_files):
    print(f"Обрабатываю {i+1}/{len(image_files)}: {img_path.name}")
    try:
        img = Image.open(img_path)
        img = img.rotate(0, expand=True)
        if hasattr(img, '_getexif') and img._getexif():
            exif = img._getexif()
            orientation = exif.get(274)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        img_data = base64.standard_b64encode(buf.getvalue()).decode('utf-8')

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_data}},
                    {"type": "text", "text": """Это скриншот вопроса из теста USCG Captain 6-Pack.
Извлеки:
1. Текст вопроса на английском
2. Варианты ответов A, B, C, D
3. Правильный ответ (обведён зелёным)
4. Есть ли на скрине схема/картинка к вопросу (да/нет)

Если это НЕ вопрос теста — ответь только: НЕ ВОПРОС

Формат ответа:
ВОПРОС: ...
A: ...
B: ...
C: ...
D: ...
ОТВЕТ: буква
КАРТИНКА: да/нет"""}
                ]
            }]
        )

        text = response.content[0].text.strip()

        if "НЕ ВОПРОС" in text:
            print(f"  → Пропускаю (не вопрос)")
            continue

        results.append(f"Вопрос {question_num}\n{text}\n\n---\n")
        question_num += 1

    except Exception as e:
        print(f"  → Ошибка: {e}")
        results.append(f"Вопрос {question_num}\n⚠️ ОШИБКА ОБРАБОТКИ: {img_path.name}\n\n---\n")
        question_num += 1

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print(f"\nГотово! Извлечено вопросов: {question_num - 131}")
print(f"Файл сохранён: {output_file}")
