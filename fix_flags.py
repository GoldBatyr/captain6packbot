with open('/Users/Batyr/Documents/exam_screens/bot.py', encoding='utf-8') as f:
    src = f.read()

replacements = {
    '🇺🇸 English answered:': 'EN English answered:',
    '🇷🇺 На русском:': 'RU На русском:',
    '🇺🇸 English:': 'EN English:',
    '🇷🇺 Russian:': 'RU Russian:',
    'By topic / По темам (🇺🇸 EN):': 'By topic / По темам (EN):',
    '🇺🇸': 'EN',
    '🇷🇺': 'RU',
}

for old, new in replacements.items():
    count = src.count(old)
    src = src.replace(old, new)
    print(f"'{old}' -> '{new}': {count} замен")

with open('/Users/Batyr/Documents/exam_screens/bot.py', 'w', encoding='utf-8') as f:
    f.write(src)
print("Done")
