import json

with open('/Users/Batyr/Documents/exam_screens/questions.json', encoding='utf-8') as f:
    data = json.load(f)

q_str = "QUESTIONS = " + json.dumps(data, ensure_ascii=False, indent=4).replace("null", "None").replace("true", "True").replace("false", "False")

rest = r"""
user_state = {}

MAIN_MENU_TEXT = "⚓ Добро пожаловать! / Welcome to Captain6PackBot!\n\nВыберите режим / Choose mode:"

TOPICS = {
    "sound_signals":   {"ru": "🔊 Звуковые сигналы",       "en": "Sound Signals"},
    "lights_shapes":   {"ru": "💡 Огни и знаки",            "en": "Lights & Shapes"},
    "steering_rules":  {"ru": "🚢 Маневрирование",          "en": "Steering Rules"},
    "narrow_channels": {"ru": "🌊 Узкие каналы",            "en": "Narrow Channels"},
    "visibility":      {"ru": "🌫️ Ограниченная видимость",  "en": "Visibility"},
    "distress":        {"ru": "🆘 Сигналы бедствия",        "en": "Distress Signals"},
    "charts":          {"ru": "🗺️ Карты и публикации",      "en": "Charts & Publications"},
    "weather":         {"ru": "🌦️ Погода",                  "en": "Weather"},
    "navigation":      {"ru": "🧭 Навигация",               "en": "Navigation"},
    "tides_currents":  {"ru": "🌊 Приливы и течения",       "en": "Tides & Currents"},
    "seamanship":      {"ru": "⚓ Морская практика",        "en": "Seamanship"},
}

GLOSSARY = [
    {"term": "Port", "ru": "Левый борт", "file_id": "CQACAgIAAxkBAAIDpmnd33oq7vcbl3C-HGPr_Y6J2b1lAAIclAACwGnxSlm-Tt506gAB5jsE"},
    {"term": "Starboard", "ru": "Правый борт", "file_id": "CQACAgIAAxkBAAIDomnd33qbRs51tSAVvE0nryvGzWbiAAIYlAACwGnxSl0Q_m9ht5HwOwQ"},
    {"term": "Underway", "ru": "На ходу", "file_id": "CQACAgIAAxkBAAIDp2nd33p35ayaxoqPNzwJYN641FA0AAIdlAACwGnxSh9PEQJydsOFOwQ"},
    {"term": "Overtaking", "ru": "Обгон", "file_id": "CQACAgIAAxkBAAIDqGnd33oW1nO6ZBHubCbuKyxT_UH0AAIelAACwGnxSsBO4PBX4-ieOwQ"},
    {"term": "Stand-on vessel", "ru": "Привилегированное судно", "file_id": "CQACAgIAAxkBAAIDo2nd33pzNbV5R2gB0i-p2r-Y7YobAAIZlAACwGnxSnvglY2QQHKVOwQ"},
    {"term": "Give-way vessel", "ru": "Уступающее судно", "file_id": "CQACAgIAAxkBAAIDpGnd33pmRKGYLIMxhkpqbMaEEHFuAAIalAACwGnxSjVVyCDZokm5OwQ"},
    {"term": "Rules of the Road", "ru": "Правила плавания", "file_id": "CQACAgIAAxkBAAIDpWnd33on0t1CyfrTMrJpL0DfoRa0AAIblAACwGnxSj3l3wm9tbZoOwQ"},
]


def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Тест / Quiz — все вопросы", callback_data="menu_quiz")],
        [InlineKeyboardButton("📚 Topics / Темы — по разделам", callback_data="menu_topics")],
        [InlineKeyboardButton("📖 Glossary / Глоссарий", callback_data="menu_glossary")],
        [InlineKeyboardButton("🔊👂 Listening / Аудирование 🚗🏋️", callback_data="menu_drive")],
        [InlineKeyboardButton("📊 My Progress / Мой прогресс", callback_data="menu_progress")],
        [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
    ])


def get_topics_keyboard():
    buttons = []
    for key, names in TOPICS.items():
        count = sum(1 for q in QUESTIONS if q.get("topic") == key)
        btn_text = f"{names['en']} / {names['ru']} ({count})"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"topic_{key}")])
    buttons.append([InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def get_topic_start_keyboard(topic_key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Start / Начать", callback_data=f"start_topic_{topic_key}")],
        [InlineKeyboardButton("📚 Topics / Темы", callback_data="menu_topics")],
        [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
    ])


def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    # Удаляем старое меню если есть
    if user_id in user_state and user_state[user_id].get("last_menu_id"):
        try:
            update.message.bot.delete_message(
                chat_id=update.message.chat_id,
                message_id=user_state[user_id]["last_menu_id"]
            )
        except Exception:
            pass
    try:
        update.message.delete()
    except Exception:
        pass
    msg = update.message.reply_text(MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())
    if user_id in user_state:
        user_state[user_id]["last_menu_id"] = msg.message_id


def send_glossary(chat_id, context, index, old_msg_id=None):
    if old_msg_id:
        try:
            context.bot.delete_message(chat_id=chat_id, message_id=old_msg_id)
        except Exception as e:
            logging.error(f"DELETE ERROR: {e}")
    if index >= len(GLOSSARY):
        context.bot.send_message(chat_id=chat_id, text=MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())
        return
    term = GLOSSARY[index]
    caption = f"📖 {index + 1} из {len(GLOSSARY)}\n\nEN: {term['term']}\nRU: {term['ru']}"
    try:
        context.bot.send_audio(
            chat_id=chat_id, audio=term["file_id"], caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Next", callback_data=f"glo_{index + 1}")],
                [InlineKeyboardButton("🏠 Меню / Menu", callback_data="main_menu_from_glo")],
            ])
        )
    except Exception as e:
        logging.error(f"SEND_AUDIO ERROR: {e}")


def strip_letter(opt_text):
    if len(opt_text) >= 3 and opt_text[1] == ")":
        return opt_text[3:].strip()
    return opt_text.strip()


def build_question_keyboard(state):
    lang = state["lang"]
    lang_btn = "🌐 English / На русском" if lang == "ru" else "🌐 Russian / На английском"
    q = QUESTIONS[state["order"][state["pos"]]]
    buttons = [
        [
            InlineKeyboardButton("A", callback_data="answer_0"),
            InlineKeyboardButton("B", callback_data="answer_1"),
            InlineKeyboardButton("C", callback_data="answer_2"),
            InlineKeyboardButton("D", callback_data="answer_3"),
        ],
        [InlineKeyboardButton(lang_btn, callback_data="toggle_lang")],
        [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
    ]
    if q.get("audio_q"):
        buttons.insert(2, [InlineKeyboardButton("▶️ Play / Слушать", callback_data="play_q")])
    return InlineKeyboardMarkup(buttons)


def send_question(query, state, context):
    for msg_id in state.get("audio_msg_ids", []):
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
        except Exception:
            pass
    state["audio_msg_ids"] = []
    q = QUESTIONS[state["order"][state["pos"]]]
    lang = state["lang"]
    question = q["ru_q"] if lang == "ru" else q["en_q"]
    options = q["ru_options"] if lang == "ru" else q["en_options"]
    options_text = "\n".join(options)
    full_text = f"❓ Вопрос {q['num']} из {len(QUESTIONS)}\n\n{question}\n\n{options_text}"
    keyboard = build_question_keyboard(state)
    if q.get("image"):
        try:
            img_msg = context.bot.send_photo(chat_id=query.message.chat_id, photo=q["image"])
            state["audio_msg_ids"].append(img_msg.message_id)
        except Exception as e:
            logging.error(f"SEND_PHOTO ERROR: {e}")
    try:
        query.edit_message_text(full_text, reply_markup=keyboard)
    except Exception:
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_message(chat_id=query.message.chat_id, text=full_text, reply_markup=keyboard)


def send_question_no_delete(query, state, context):
    q = QUESTIONS[state["order"][state["pos"]]]
    lang = state["lang"]
    question = q["ru_q"] if lang == "ru" else q["en_q"]
    options = q["ru_options"] if lang == "ru" else q["en_options"]
    options_text = "\n".join(options)
    full_text = f"❓ Вопрос {q['num']} из {len(QUESTIONS)}\n\n{question}\n\n{options_text}"
    keyboard = build_question_keyboard(state)
    try:
        query.edit_message_text(full_text, reply_markup=keyboard)
    except Exception:
        pass


def get_file_id(update: Update, context: CallbackContext):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        update.message.reply_text(f"🖼 Photo file_id:\n<code>{file_id}</code>", parse_mode="HTML")
    elif update.message.audio:
        update.message.reply_text(f"🔊 {update.message.audio.file_name}:\n<code>{update.message.audio.file_id}</code>", parse_mode="HTML")
    elif update.message.document:
        update.message.reply_text(f"📎 {update.message.document.file_name}:\n<code>{update.message.document.file_id}</code>", parse_mode="HTML")


def send_progress_snapshot(chat_id, context, state):
    total = len(QUESTIONS)
    en_done = len(state["progress_en"])
    ru_done = len(state["progress_ru"])
    audio_done = len(state["progress_audio"])
    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    date_str = now.strftime("%d %b %Y")

    def bar(count, total):
        filled = round(count / total * 10) if total > 0 else 0
        return "▓" * filled + "░" * (10 - filled)

    topic_lines = []
    for key, names in TOPICS.items():
        topic_nums = set(q["num"] for q in QUESTIONS if q.get("topic") == key)
        topic_total = len(topic_nums)
        topic_done = len(state["progress_en"] & topic_nums)
        if topic_total == 0:
            continue
        icon = "✅" if topic_done == topic_total else ("🔄" if topic_done > 0 else "⬜")
        topic_lines.append(f"{icon} {names['en']}: {topic_done}/{topic_total}")

    topics_text = "\n".join(topic_lines)
    last = state.get("last_snapshot")
    if last is None:
        delta_text = f"📅 {date_str}\nFirst snapshot / Первый снапшот"
    else:
        delta_text = (
            f"📅 {date_str} — since last time / с прошлого раза:\n"
            f"EN: +{en_done - last['en']}\n"
            f"RU: +{ru_done - last['ru']}\n"
            f"🎧 Audio: +{audio_done - last['audio']}"
        )

    text = (
        f"📊 My Progress / Мой прогресс\n\n"
        f"EN answered:  {en_done} / {total}\n"
        f"{bar(en_done, total)}\n\n"
        f"RU answered:  {ru_done} / {total}\n"
        f"{bar(ru_done, total)}\n\n"
        f"Audio listened:  {audio_done} / {total}\n"
        f"{bar(audio_done, total)}\n\n"
        f"By topic / По темам (EN):\n"
        f"{topics_text}\n\n"
        f"{'─' * 20}\n"
        f"{delta_text}"
    )
    state["last_snapshot"] = {"en": en_done, "ru": ru_done, "audio": audio_done}
    context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu_from_progress")]]))


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    if user_id not in user_state:
        order = list(range(len(QUESTIONS)))
        random.shuffle(order)
        user_state[user_id] = {
            "lang": "ru", "pos": 0, "g_index": 0, "order": order, "audio_msg_ids": [],
            "progress_en": set(), "progress_ru": set(), "progress_audio": set(), "last_snapshot": None, "last_menu_id": None,
        }
    state = user_state[user_id]
    for key in ["audio_msg_ids", "progress_en", "progress_ru", "progress_audio"]:
        if key not in state:
            state[key] = [] if key == "audio_msg_ids" else set()
    if "last_snapshot" not in state:
        state["last_snapshot"] = None

    if query.data in ("main_menu", "main_menu_from_glo"):
        for msg_id in state.get("audio_msg_ids", []):
            try:
                context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
            except Exception:
                pass
        state["audio_msg_ids"] = []
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_message(chat_id=query.message.chat_id, text=MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())

    elif query.data == "main_menu_from_progress":
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_message(chat_id=query.message.chat_id, text=MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())

    elif query.data == "menu_quiz":
        order = list(range(len(QUESTIONS)))
        random.shuffle(order)
        state["order"] = order
        state["pos"] = 0
        send_question(query, state, context)

    elif query.data == "menu_topics":
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_message(chat_id=query.message.chat_id, text="📚 Choose topic / Выберите тему:", reply_markup=get_topics_keyboard())

    elif query.data.startswith("topic_"):
        topic_key = query.data[6:]
        topic = TOPICS.get(topic_key, {})
        count = sum(1 for q in QUESTIONS if q.get("topic") == topic_key)
        text = f"{topic.get('en', '')} / {topic.get('ru', '')}\n\n{count} questions / {count} вопросов\n\nQuestions on this topic only / Вопросы только по этой теме"
        try:
            query.edit_message_text(text, reply_markup=get_topic_start_keyboard(topic_key))
        except Exception:
            pass

    elif query.data.startswith("start_topic_"):
        topic_key = query.data[12:]
        topic_order = [i for i, q in enumerate(QUESTIONS) if q.get("topic") == topic_key]
        random.shuffle(topic_order)
        state["order"] = topic_order
        state["pos"] = 0
        send_question(query, state, context)

    elif query.data == "toggle_lang":
        state["lang"] = "en" if state["lang"] == "ru" else "ru"
        send_question_no_delete(query, state, context)

    elif query.data == "play_q":
        q = QUESTIONS[state["order"][state["pos"]]]
        if q.get("audio_q"):
            msg = context.bot.send_audio(chat_id=query.message.chat_id, audio=q["audio_q"])
            state["audio_msg_ids"].append(msg.message_id)
            state["progress_audio"].add(q["num"])

    elif query.data == "play_a":
        q = QUESTIONS[state["order"][state["pos"]]]
        if q.get("audio_a"):
            msg = context.bot.send_audio(chat_id=query.message.chat_id, audio=q["audio_a"])
            state["audio_msg_ids"].append(msg.message_id)
            state["progress_audio"].add(q["num"])

    elif query.data.startswith("answer_"):
        chosen = int(query.data.split("_")[1])
        q = QUESTIONS[state["order"][state["pos"]]]
        lang = state["lang"]
        q_num = q["num"]
        if q_num not in state["progress_en"] and q_num not in state["progress_ru"]:
            if lang == "en":
                state["progress_en"].add(q_num)
            else:
                state["progress_ru"].add(q_num)
        explain = q["ru_explain"] if lang == "ru" else q["en_explain"]
        correct_idx = q["correct"]
        options = q["ru_options"] if lang == "ru" else q["en_options"]
        correct_answer_text = strip_letter(options[correct_idx])
        if chosen == correct_idx:
            result = f"✅ Правильно! / Correct!\n\n📌 {correct_answer_text}\n\n{explain}"
        else:
            chosen_answer_text = strip_letter(options[chosen])
            result = f"❌ Неверно! / Wrong!\n\nВаш ответ: {chosen_answer_text}\nПравильный ответ: {correct_answer_text}\n\n{explain}"
        lang_btn = "🌐 English / На русском" if lang == "ru" else "🌐 Russian / На английском"
        buttons = [
            [InlineKeyboardButton("⬅️ Back / Назад", callback_data="back_to_question"),
             InlineKeyboardButton("➡️ Next / Далее", callback_data="next_question")],
            [InlineKeyboardButton(lang_btn, callback_data="toggle_lang_answer")],
            [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
        ]
        if q.get("audio_a"):
            buttons.insert(1, [InlineKeyboardButton("▶️ Play / Слушать", callback_data="play_a")])
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "back_to_question":
        send_question(query, state, context)

    elif query.data == "toggle_lang_answer":
        state["lang"] = "en" if state["lang"] == "ru" else "ru"
        q = QUESTIONS[state["order"][state["pos"]]]
        lang = state["lang"]
        explain = q["ru_explain"] if lang == "ru" else q["en_explain"]
        correct_idx = q["correct"]
        options = q["ru_options"] if lang == "ru" else q["en_options"]
        correct_answer_text = strip_letter(options[correct_idx])
        lang_btn = "🌐 English / На русском" if lang == "ru" else "🌐 Russian / На английском"
        result = f"💡 Правильный ответ: {correct_answer_text}\n\n{explain}"
        buttons = [
            [InlineKeyboardButton("⬅️ Back / Назад", callback_data="back_to_question"),
             InlineKeyboardButton("➡️ Next / Далее", callback_data="next_question")],
            [InlineKeyboardButton(lang_btn, callback_data="toggle_lang_answer")],
            [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
        ]
        if q.get("audio_a"):
            buttons.insert(1, [InlineKeyboardButton("▶️ Play / Слушать", callback_data="play_a")])
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "next_question":
        next_pos = state["pos"] + 1
        if next_pos >= len(state["order"]):
            current_topic = None
            if len(state["order"]) < len(QUESTIONS):
                first_q = QUESTIONS[state["order"][0]]
                current_topic = first_q.get("topic")
            if current_topic and current_topic in TOPICS:
                topic = TOPICS[current_topic]
                count = len(state["order"])
                text = f"🎉 Topic complete! / Тема завершена!\n\n{topic['en']} / {topic['ru']}\n\n✅ {count} questions done / {count} вопросов пройдено\n\nWhat's next? / Что дальше?"
                buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Repeat / Повторить", callback_data=f"start_topic_{current_topic}")],
                    [InlineKeyboardButton("📚 Topics / Темы", callback_data="menu_topics")],
                    [InlineKeyboardButton("📝 All questions / Все вопросы", callback_data="menu_quiz")],
                    [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
                ])
                query.edit_message_text(text, reply_markup=buttons)
            else:
                state["pos"] = 0
                send_question(query, state, context)
        else:
            state["pos"] = next_pos
            send_question(query, state, context)

    elif query.data == "menu_glossary":
        state["g_index"] = 0
        send_glossary(query.message.chat_id, context, 0, old_msg_id=query.message.message_id)

    elif query.data.startswith("glo_"):
        index = int(query.data[4:])
        state["g_index"] = index
        send_glossary(query.message.chat_id, context, index, old_msg_id=query.message.message_id)

    elif query.data == "menu_progress":
        try:
            query.message.delete()
        except Exception:
            pass
        send_progress_snapshot(query.message.chat_id, context, state)

    elif query.data == "menu_drive":
        query.edit_message_text(
            "🔊👂 Режим аудирования в разработке / Listening mode coming soon! 🚗 🏋️",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")]])
        )


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.photo | Filters.audio | Filters.document, get_file_id))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
"""

header = """# -*- coding: utf-8 -*-
import logging
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
import os
TOKEN = os.environ.get("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

"""

with open('/Users/Batyr/Documents/exam_screens/bot.py', 'w', encoding='utf-8') as f:
    f.write(header)
    f.write(q_str)
    f.write('\n')
    f.write(rest)

print('bot.py готов!')
import ast
with open('/Users/Batyr/Documents/exam_screens/bot.py', encoding='utf-8') as f:
    src = f.read()
try:
    ast.parse(src)
    print('Синтаксис OK')
except SyntaxError as e:
    print(f'Ошибка: {e}')
