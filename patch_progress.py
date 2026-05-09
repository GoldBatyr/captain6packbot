with open('/Users/Batyr/Documents/exam_screens/build_bot.py', encoding='utf-8') as f:
    src = f.read()

old = '    context.bot.send_message(chat_id=chat_id, text=text)\n    context.bot.send_message(chat_id=chat_id, text=MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())'

new = '    context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu_from_progress")]]))'

if old in src:
    src = src.replace(old, new)
    with open('/Users/Batyr/Documents/exam_screens/build_bot.py', 'w', encoding='utf-8') as f:
        f.write(src)
    print("OK - patched")
else:
    print("NOT FOUND")
