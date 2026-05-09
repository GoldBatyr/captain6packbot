with open('/Users/Batyr/Documents/exam_screens/bot.py', encoding='utf-8') as f:
    src = f.read()

old = 'callback_data="main_menu_from_progress")])]\n\n    elif query.data == "main_menu_from_progress":\n        context.bot.send_message(\n            chat_id=query.message.chat_id,\n            text=MAIN_MENU_TEXT,\n            reply_markup=get_main_menu_keyboard()\n        )'

new = 'callback_data="main_menu_from_progress")])]\n\n    elif query.data == "main_menu_from_progress":\n        try:\n            query.message.delete()\n        except Exception:\n            pass\n        context.bot.send_message(\n            chat_id=query.message.chat_id,\n            text=MAIN_MENU_TEXT,\n            reply_markup=get_main_menu_keyboard()\n        )'

if old in src:
    src = src.replace(old, new)
    with open('/Users/Batyr/Documents/exam_screens/bot.py', 'w', encoding='utf-8') as f:
        f.write(src)
    print("OK")
else:
    # Find exact context
    idx = src.find('main_menu_from_progress')
    while idx != -1:
        print(f"--- pos {idx} ---")
        print(repr(src[idx:idx+150]))
        idx = src.find('main_menu_from_progress', idx+1)
