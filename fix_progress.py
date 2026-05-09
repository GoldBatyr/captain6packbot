with open('/Users/Batyr/Documents/exam_screens/bot.py', encoding='utf-8') as f:
    src = f.read()

old = '    elif query.data == "main_menu_from_progress":\n        context.bot.send_message(chat_id=query.message.chat_id, text=MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())\n'

new = '    elif query.data == "main_menu_from_progress":\n        try:\n            query.message.delete()\n        except Exception:\n            pass\n        context.bot.send_message(chat_id=query.message.chat_id, text=MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())\n'

if old in src:
    src = src.replace(old, new)
    with open('/Users/Batyr/Documents/exam_screens/bot.py', 'w', encoding='utf-8') as f:
        f.write(src)
    print("OK")
else:
    print("NOT FOUND")
