import json

with open('/Users/Batyr/Documents/exam_screens/questions.json', encoding='utf-8') as f:
    data = json.load(f)

# Fix topics for chart navigation questions
CHART_QUESTIONS = {341, 342, 343, 344, 345, 346, 356, 363}
for q in data:
    if q.get("num") in CHART_QUESTIONS:
        q["topic"] = "navigation"

q_str = "QUESTIONS = " + json.dumps(data, ensure_ascii=False, indent=4).replace("null", "None").replace("true", "True").replace("false", "False")

rest = (
    'import sqlite3\n'
    'import threading\n'
    '\n'
    'DB_PATH = os.environ.get("DB_PATH", "/data/progress.db")\n'
    'DB_LOCK = threading.Lock()\n'
    'ADMIN_ID = 5291782708\n'
    'SUSPICIOUS_THRESHOLD = 30\n'
    'SUSPICIOUS_MINUTES = 5\n'
    '\n'
    'def init_db():\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_seen TEXT, last_seen TEXT, source TEXT, is_paid INTEGER DEFAULT 0, is_banned INTEGER DEFAULT 0, questions_answered INTEGER DEFAULT 0)")\n'
    '        try:\n'
    '            c.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")\n'
    '        except Exception:\n'
    '            pass\n'
    '        try:\n'
    '            c.execute("ALTER TABLE users ADD COLUMN is_paid INTEGER DEFAULT 0")\n'
    '        except Exception:\n'
    '            pass\n'
    '        try:\n'
    '            c.execute("ALTER TABLE users ADD COLUMN questions_answered INTEGER DEFAULT 0")\n'
    '        except Exception:\n'
    '            pass\n'
    '        c.execute("CREATE TABLE IF NOT EXISTS progress (user_id INTEGER PRIMARY KEY, progress_en TEXT DEFAULT \'\', progress_ru TEXT DEFAULT \'\', progress_audio TEXT DEFAULT \'\', last_snapshot_en INTEGER DEFAULT 0, last_snapshot_ru INTEGER DEFAULT 0, last_snapshot_audio INTEGER DEFAULT 0)")\n'
    '        c.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, event_type TEXT, detail TEXT, created_at TEXT)")\n'
    '        conn.commit()\n'
    '        conn.close()\n'
    '\n'
    'def db_upsert_user(user_id, username, source=None):\n'
    '    now = datetime.now(ZoneInfo("America/Los_Angeles")).isoformat()\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))\n'
    '        if c.fetchone():\n'
    '            c.execute("UPDATE users SET last_seen=?, username=? WHERE user_id=?", (now, username, user_id))\n'
    '        else:\n'
    '            c.execute("INSERT INTO users (user_id, username, first_seen, last_seen, source) VALUES (?,?,?,?,?)", (user_id, username, now, now, source or "direct"))\n'
    '            c.execute("INSERT OR IGNORE INTO progress (user_id) VALUES (?)", (user_id,))\n'
    '        conn.commit()\n'
    '        conn.close()\n'
    '\n'
    'def db_is_banned(user_id):\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("SELECT is_banned FROM users WHERE user_id=?", (user_id,))\n'
    '        row = c.fetchone()\n'
    '        conn.close()\n'
    '    return row and row[0] == 1\n'
    '\n'
    'def db_is_paid(user_id):\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("SELECT is_paid FROM users WHERE user_id=?", (user_id,))\n'
    '        row = c.fetchone()\n'
    '        conn.close()\n'
    '    return row and row[0] == 1\n'
    '\n'
    'def db_set_paid(user_id, paid=True):\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("UPDATE users SET is_paid=? WHERE user_id=?", (1 if paid else 0, user_id))\n'
    '        conn.commit()\n'
    '        conn.close()\n'
    '\n'
    'def db_ban_user(user_id, banned=True):\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("UPDATE users SET is_banned=? WHERE user_id=?", (1 if banned else 0, user_id))\n'
    '        conn.commit()\n'
    '        conn.close()\n'
    '\n'
    'def db_log_event(user_id, event_type, detail=""):\n'
    '    now = datetime.now(ZoneInfo("America/Los_Angeles")).isoformat()\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("INSERT INTO events (user_id, event_type, detail, created_at) VALUES (?,?,?,?)", (user_id, event_type, detail, now))\n'
    '        conn.commit()\n'
    '        conn.close()\n'
    '\n'
    'def db_check_suspicious(user_id):\n'
    '    now = datetime.now(ZoneInfo("America/Los_Angeles"))\n'
    '    cutoff = now.replace(minute=max(0, now.minute - SUSPICIOUS_MINUTES)).isoformat()\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("SELECT COUNT(*) FROM events WHERE user_id=? AND event_type=\'answer\' AND created_at >= ?", (user_id, cutoff))\n'
    '        count = c.fetchone()[0]\n'
    '        conn.close()\n'
    '    return count >= SUSPICIOUS_THRESHOLD\n'
    '\n'
    'def db_save_progress(user_id, progress_en, progress_ru, progress_audio):\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        en_str = ",".join(str(x) for x in progress_en)\n'
    '        ru_str = ",".join(str(x) for x in progress_ru)\n'
    '        audio_str = ",".join(str(x) for x in progress_audio)\n'
    '        c.execute("INSERT INTO progress (user_id, progress_en, progress_ru, progress_audio) VALUES (?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET progress_en=excluded.progress_en, progress_ru=excluded.progress_ru, progress_audio=excluded.progress_audio", (user_id, en_str, ru_str, audio_str))\n'
    '        c.execute("UPDATE users SET questions_answered=? WHERE user_id=?", (len(progress_en) + len(progress_ru), user_id))\n'
    '        conn.commit()\n'
    '        conn.close()\n'
    '\n'
    'def db_load_progress(user_id):\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("SELECT progress_en, progress_ru, progress_audio, last_snapshot_en, last_snapshot_ru, last_snapshot_audio FROM progress WHERE user_id=?", (user_id,))\n'
    '        row = c.fetchone()\n'
    '        conn.close()\n'
    '    if not row:\n'
    '        return set(), set(), set(), None\n'
    '    def parse(s):\n'
    '        return set(int(x) for x in s.split(",") if x.strip())\n'
    '    en = parse(row[0])\n'
    '    ru = parse(row[1])\n'
    '    audio = parse(row[2])\n'
    '    snapshot = {"en": row[3], "ru": row[4], "audio": row[5]} if (row[3] or row[4] or row[5]) else None\n'
    '    return en, ru, audio, snapshot\n'
    '\n'
    'def db_save_snapshot(user_id, en, ru, audio):\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("UPDATE progress SET last_snapshot_en=?, last_snapshot_ru=?, last_snapshot_audio=? WHERE user_id=?", (en, ru, audio, user_id))\n'
    '        conn.commit()\n'
    '        conn.close()\n'
    '\n'
    'def db_get_users(limit=50):\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("SELECT user_id, username, first_seen, last_seen, is_paid, is_banned, questions_answered FROM users ORDER BY last_seen DESC LIMIT ?", (limit,))\n'
    '        rows = c.fetchall()\n'
    '        conn.close()\n'
    '    return rows\n'
    '\n'
    'def db_get_stats():\n'
    '    now = datetime.now(ZoneInfo("America/Los_Angeles"))\n'
    '    today = now.strftime("%Y-%m-%d")\n'
    '    week_ago = now.replace(day=max(1, now.day - 7)).isoformat()\n'
    '    with DB_LOCK:\n'
    '        conn = sqlite3.connect(DB_PATH)\n'
    '        c = conn.cursor()\n'
    '        c.execute("SELECT COUNT(*) FROM users WHERE is_banned=0")\n'
    '        total = c.fetchone()[0]\n'
    '        c.execute("SELECT COUNT(*) FROM users WHERE first_seen LIKE ? AND is_banned=0", (today + "%",))\n'
    '        new_today = c.fetchone()[0]\n'
    '        c.execute("SELECT COUNT(*) FROM users WHERE last_seen >= ? AND is_banned=0", (week_ago,))\n'
    '        active_week = c.fetchone()[0]\n'
    '        c.execute("SELECT COUNT(*) FROM users WHERE is_paid=1")\n'
    '        paid = c.fetchone()[0]\n'
    '        c.execute("SELECT COUNT(*) FROM users WHERE is_banned=1")\n'
    '        banned = c.fetchone()[0]\n'
    '        c.execute("SELECT COUNT(DISTINCT user_id) FROM events WHERE event_type=\'paywall\'")\n'
    '        hit_paywall = c.fetchone()[0]\n'
    '        c.execute("SELECT detail, COUNT(*) as cnt FROM events WHERE event_type=\'topic\' GROUP BY detail ORDER BY cnt DESC LIMIT 5")\n'
    '        top_topics = c.fetchall()\n'
    '        c.execute("SELECT COUNT(DISTINCT user_id) FROM users WHERE last_seen < ? AND questions_answered > 0 AND is_banned=0", (week_ago,))\n'
    '        sleeping = c.fetchone()[0]\n'
    '        conn.close()\n'
    '    conv_paywall = str(round(hit_paywall / total * 100)) + "%" if total > 0 else "0%"\n'
    '    conv_paid = str(round(paid / hit_paywall * 100)) + "%" if hit_paywall > 0 else "0%"\n'
    '    topics_text = ""\n'
    '    for t, cnt in top_topics:\n'
    '        name = TOPICS.get(t, {}).get("en", t)\n'
    '        topics_text += "\\n  * " + name + ": " + str(cnt)\n'
    '    return (\n'
    '        "\\U0001f4ca Stats Captain6PackBot\\n"\n'
    '        + "-" * 25 + "\\n"\n'
    '        + "\\U0001f465 Total users: " + str(total) + "\\n"\n'
    '        + "\\U0001f195 New today: " + str(new_today) + "\\n"\n'
    '        + "\\U0001f525 Active 7 days: " + str(active_week) + "\\n"\n'
    '        + "\\U0001f634 Sleeping (7+ days): " + str(sleeping) + "\\n"\n'
    '        + "\\U0001f4b0 Paid: " + str(paid) + "\\n"\n'
    '        + "\\U0001f6ab Banned: " + str(banned) + "\\n"\n'
    '        + "-" * 25 + "\\n"\n'
    '        + "\\U0001f3af Funnel:\\n"\n'
    '        + "  Hit paywall: " + str(hit_paywall) + " (" + conv_paywall + ")\\n"\n'
    '        + "  Of those paid: " + str(paid) + " (" + conv_paid + ")\\n"\n'
    '        + "-" * 25 + "\\n"\n'
    '        + "\\U0001f3c6 Top topics:" + topics_text + "\\n"\n'
    '        + "-" * 25 + "\\n"\n'
    '        + now.strftime("%d %b %Y %H:%M") + " PT"\n'
    '    )\n'
    '\n'
    'user_state = {}\n'
)

rest2 = r"""
MAIN_MENU_TEXT = "⚓ Добро пожаловать! / Welcome to Captain6PackBot!\n\nВыберите режим / Choose mode:"
COPYRIGHT = "© Captain6PackBot · Все права защищены / All rights reserved"
START_COPYRIGHT = (
    "\n\n⚠️ Копирование, пересылка и распространение материалов бота "
    "запрещено и является нарушением авторских прав.\n"
    "Copying, forwarding or distributing bot content is prohibited "
    "under Copyright Act (17 U.S.C.)."
)

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


def get_or_init_state(user_id):
    if user_id not in user_state:
        order = list(range(len(QUESTIONS)))
        random.shuffle(order)
        en, ru, audio, snapshot = db_load_progress(user_id)
        user_state[user_id] = {
            "lang": "ru", "pos": 0, "g_index": 0, "order": order,
            "audio_msg_ids": [],
            "progress_en": en,
            "progress_ru": ru,
            "progress_audio": audio,
            "last_snapshot": snapshot,
            "last_menu_id": None,
        }
    return user_state[user_id]


def notify_admin(context, text):
    try:
        context.bot.send_message(chat_id=ADMIN_ID, text=text)
    except Exception as e:
        logging.error(f"NOTIFY_ADMIN ERROR: {e}")


def start(update, context):
    user = update.message.from_user
    user_id = user.id
    username = user.username or user.first_name or str(user_id)
    args = context.args
    source = args[0] if args else "direct"
    if db_is_banned(user_id):
        update.message.reply_text("🚫 Ваш аккаунт заблокирован за нарушение правил использования.\nYour account has been banned for violating terms of use.")
        return
    db_upsert_user(user_id, username, source)
    db_log_event(user_id, "start", source)
    state = get_or_init_state(user_id)
    if state.get("last_menu_id"):
        try:
            update.message.bot.delete_message(chat_id=update.message.chat_id, message_id=state["last_menu_id"])
        except Exception:
            pass
    try:
        update.message.delete()
    except Exception:
        pass
    msg = update.message.reply_text(MAIN_MENU_TEXT + START_COPYRIGHT, reply_markup=get_main_menu_keyboard())
    state["last_menu_id"] = msg.message_id


def cmd_stats(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        update.message.delete()
    except Exception:
        pass
    context.bot.send_message(chat_id=update.message.chat_id, text=db_get_stats())


def cmd_users(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        update.message.delete()
    except Exception:
        pass
    rows = db_get_users(50)
    if not rows:
        context.bot.send_message(chat_id=update.message.chat_id, text="Пользователей пока нет.")
        return
    lines = ["👥 Пользователи Captain6PackBot\n" + "-" * 30]
    for i, (uid, uname, first, last, paid, banned, answered) in enumerate(rows, 1):
        uname_str = "@" + uname if uname else "no username"
        status = "🚫" if banned else ("💰" if paid else "🆓")
        first_short = first[:10] if first else "?"
        last_short = last[:10] if last else "?"
        lines.append(f"{i}. {status} {uname_str}\n   ID: {uid}\n   Joined: {first_short} | Last: {last_short}\n   Questions: {answered}")
    text = "\n\n".join(lines)
    for i in range(0, len(text), 4000):
        context.bot.send_message(chat_id=update.message.chat_id, text=text[i:i+4000])


def cmd_send(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /send <user_id> <text>")
        return
    try:
        target_id = int(args[0])
        text = " ".join(args[1:])
        context.bot.send_message(chat_id=target_id, text=f"📬 Сообщение от Captain6PackBot:\n\n{text}")
        update.message.reply_text(f"✅ Отправлено пользователю {target_id}")
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")


def cmd_ban(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return
    args = context.args
    if not args:
        update.message.reply_text("Usage: /ban <user_id>")
        return
    try:
        target_id = int(args[0])
        db_ban_user(target_id, True)
        try:
            context.bot.send_message(chat_id=target_id, text="🚫 Ваш аккаунт заблокирован за нарушение правил использования.\nYour account has been banned for violating terms of use.")
        except Exception:
            pass
        update.message.reply_text(f"✅ Пользователь {target_id} заблокирован.")
        db_log_event(target_id, "banned", "by_admin")
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")


def cmd_ok(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return
    args = context.args
    if not args:
        update.message.reply_text("Usage: /ok <user_id>")
        return
    try:
        target_id = int(args[0])
        db_ban_user(target_id, False)
        update.message.reply_text(f"✅ Пользователь {target_id} разблокирован.")
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")


def cmd_beta(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return
    args = context.args
    if not args:
        update.message.reply_text("Usage: /beta <user_id>")
        return
    try:
        target_id = int(args[0])
        db_set_beta(target_id, True)
        try:
            context.bot.send_message(chat_id=target_id, text="✅ Вам открыт полный доступ к боту!\nFull access granted!")
        except Exception:
            pass
        update.message.reply_text(f"✅ Полный доступ выдан пользователю {target_id}")
        db_log_event(target_id, "beta_granted", "by_admin")
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")


def cmd_unbeta(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return
    args = context.args
    if not args:
        update.message.reply_text("Usage: /unbeta <user_id>")
        return
    try:
        target_id = int(args[0])
        db_set_beta(target_id, False)
        update.message.reply_text(f"✅ Полный доступ отозван у пользователя {target_id}")
        db_log_event(target_id, "beta_revoked", "by_admin")
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")


def cmd_broadcast(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return
    text = " ".join(context.args)
    if not text:
        update.message.reply_text("Usage: /broadcast <text>")
        return
    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE is_banned=0")
        ids = [row[0] for row in c.fetchall()]
        conn.close()
    sent = 0
    failed = 0
    for uid in ids:
        try:
            context.bot.send_message(chat_id=uid, text=text)
            sent += 1
        except Exception:
            failed += 1
    update.message.reply_text(f"✅ Отправлено: {sent}\n❌ Не доставлено: {failed}")


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
    caption = f"📖 {index + 1} из {len(GLOSSARY)}\n\nEN: {term['term']}\nRU: {term['ru']}\n\n{COPYRIGHT}"
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
    return opt_text[3:].strip()


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
        buttons.insert(2, [InlineKeyboardButton("▶️ Listen/Слушать вопрос🇺🇸", callback_data="play_q")])
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
    full_text = f"❓ Вопрос {q['num']} из {len(QUESTIONS)}\n\n{question}\n\n{options_text}\n\n{COPYRIGHT}"
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
    full_text = f"❓ Вопрос {q['num']} из {len(QUESTIONS)}\n\n{question}\n\n{options_text}\n\n{COPYRIGHT}"
    keyboard = build_question_keyboard(state)
    try:
        query.edit_message_text(full_text, reply_markup=keyboard)
    except Exception:
        pass


def get_file_id(update, context):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        update.message.reply_text(f"🖼 Photo file_id:\n<code>{file_id}</code>", parse_mode="HTML")
    elif update.message.audio:
        update.message.reply_text(f"🔊 {update.message.audio.file_name}:\n<code>{update.message.audio.file_id}</code>", parse_mode="HTML")
    elif update.message.document:
        update.message.reply_text(f"📎 {update.message.document.file_name}:\n<code>{update.message.document.file_id}</code>", parse_mode="HTML")


def send_progress_snapshot(chat_id, context, state, user_id):
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
            f"Audio: +{audio_done - last['audio']}"
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
    db_save_snapshot(user_id, en_done, ru_done, audio_done)
    context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu_from_progress")]]))


def button(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    user_id = user.id
    username = user.username or user.first_name or str(user_id)

    if db_is_banned(user_id):
        query.edit_message_text("🚫 Ваш аккаунт заблокирован.\nYour account has been banned.")
        return

    db_upsert_user(user_id, username)
    state = get_or_init_state(user_id)

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
        db_log_event(user_id, "quiz_start", "all")
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
        db_log_event(user_id, "topic", topic_key)
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
            db_save_progress(user_id, state["progress_en"], state["progress_ru"], state["progress_audio"])

    elif query.data == "play_a":
        q = QUESTIONS[state["order"][state["pos"]]]
        if q.get("audio_a"):
            msg = context.bot.send_audio(chat_id=query.message.chat_id, audio=q["audio_a"])
            state["audio_msg_ids"].append(msg.message_id)
            state["progress_audio"].add(q["num"])
            db_save_progress(user_id, state["progress_en"], state["progress_ru"], state["progress_audio"])

    elif query.data.startswith("answer_"):
        chosen = int(query.data.split("_")[1])
        q = QUESTIONS[state["order"][state["pos"]]]
        lang = state["lang"]
        q_num = q["num"]
        total_answered = len(state["progress_en"]) + len(state["progress_ru"])
        if total_answered >= 8 and not db_is_paid(user_id):
            db_log_event(user_id, "paywall", str(q_num))
            query.edit_message_text(
                "🔒 Бот уже на финишной прямой, скоро запускаемся!\nСледите за рекламой.\n\nХотите ранний доступ? Напишите нам: @SurfWhisperer\n\nFull access launching soon!\nStay tuned!\nEarly access? Contact us: @SurfWhisperer",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")]])
            )
            return
        if q_num not in state["progress_en"] and q_num not in state["progress_ru"]:
            if lang == "en":
                state["progress_en"].add(q_num)
            else:
                state["progress_ru"].add(q_num)
        db_save_progress(user_id, state["progress_en"], state["progress_ru"], state["progress_audio"])
        db_log_event(user_id, "answer", f"{q_num}:{'correct' if chosen == q['correct'] else 'wrong'}")
        if db_check_suspicious(user_id):
            uname_str = "@" + username if username else str(user_id)
            notify_admin(context,
                f"⚠️ Подозрительная активность!\n"
                f"Пользователь {uname_str} прошёл {SUSPICIOUS_THRESHOLD}+ вопросов за {SUSPICIOUS_MINUTES} минут\n"
                f"ID: {user_id}\n\n"
                f"/ban {user_id} — заблокировать\n"
                f"/ok {user_id} — игнорировать"
            )
        explain = q["ru_explain"] if lang == "ru" else q["en_explain"]
        correct_idx = q["correct"]
        options = q["ru_options"] if lang == "ru" else q["en_options"]
        correct_answer_text = strip_letter(options[correct_idx])
        if chosen == correct_idx:
            result = f"✅ Правильно! / Correct!\n\n📌 {correct_answer_text}\n\n{explain}\n\n{COPYRIGHT}"
        else:
            chosen_answer_text = strip_letter(options[chosen])
            result = f"❌ Неверно! / Wrong!\n\nВаш ответ: {chosen_answer_text}\nПравильный ответ: {correct_answer_text}\n\n{explain}\n\n{COPYRIGHT}"
        lang_btn = "🌐 English / На русском" if lang == "ru" else "🌐 Russian / На английском"
        buttons = [
            [InlineKeyboardButton("⬅️ Back / Назад", callback_data="back_to_question"),
             InlineKeyboardButton("➡️ Next / Далее", callback_data="next_question")],
            [InlineKeyboardButton(lang_btn, callback_data="toggle_lang_answer")],
            [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
        ]
        if q.get("audio_a"):
            buttons.insert(1, [InlineKeyboardButton("▶️ Listen/Слушать ответ🇺🇸", callback_data="play_a")])
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
        result = f"💡 Правильный ответ: {correct_answer_text}\n\n{explain}\n\n{COPYRIGHT}"
        buttons = [
            [InlineKeyboardButton("⬅️ Back / Назад", callback_data="back_to_question"),
             InlineKeyboardButton("➡️ Next / Далее", callback_data="next_question")],
            [InlineKeyboardButton(lang_btn, callback_data="toggle_lang_answer")],
            [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
        ]
        if q.get("audio_a"):
            buttons.insert(1, [InlineKeyboardButton("▶️ Listen/Слушать ответ🇺🇸", callback_data="play_a")])
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
        total_answered = len(state["progress_en"]) + len(state["progress_ru"])
        if total_answered >= 8 and not db_is_paid(user_id):
            db_log_event(user_id, "paywall", "glossary")
            query.edit_message_text(
                "🔒 Бот уже на финишной прямой, скоро запускаемся!\nСледите за рекламой.\n\nХотите ранний доступ? Напишите нам: @SurfWhisperer\n\nFull access launching soon!\nStay tuned!\nEarly access? Contact us: @SurfWhisperer",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")]])
            )
            return
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
        send_progress_snapshot(query.message.chat_id, context, state, user_id)

    elif query.data == "menu_drive":
        query.edit_message_text(
            "🔊👂 Listening mode coming soon! 🚗 🏋️",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")]])
        )


def main():
    init_db()
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Set commands: only /start for users, all commands for admin
    from telegram import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeChat
    user_commands = [BotCommand("start", "Главное меню")]
    admin_commands = [
        BotCommand("start", "Главное меню"),
        BotCommand("stats", "Статистика (только админ)"),
        BotCommand("users", "Список пользователей (только админ)"),
        BotCommand("send", "Написать юзеру (только админ)"),
        BotCommand("ban", "Заблокировать юзера (только админ)"),
        BotCommand("ok", "Разблокировать юзера (только админ)"),
        BotCommand("beta", "Выдать полный доступ (только админ)"),
        BotCommand("unbeta", "Отозвать полный доступ (только админ)"),
        BotCommand("broadcast", "Рассылка всем (только админ)"),
    ]
    try:
        updater.bot.set_my_commands(user_commands, scope=BotCommandScopeAllPrivateChats())
        updater.bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=ADMIN_ID))
    except Exception as e:
        logging.error(f"SET_COMMANDS ERROR: {e}")

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stats", cmd_stats))
    dp.add_handler(CommandHandler("users", cmd_users))
    dp.add_handler(CommandHandler("send", cmd_send))
    dp.add_handler(CommandHandler("ban", cmd_ban))
    dp.add_handler(CommandHandler("ok", cmd_ok))
    dp.add_handler(CommandHandler("beta", cmd_beta))
    dp.add_handler(CommandHandler("unbeta", cmd_unbeta))
    dp.add_handler(CommandHandler("broadcast", cmd_broadcast))
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
import sqlite3
import threading
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
    f.write(rest2)

print('bot.py готов!')
import ast
with open('/Users/Batyr/Documents/exam_screens/bot.py', encoding='utf-8') as f:
    src = f.read()
try:
    ast.parse(src)
    print('Синтаксис OK')
except SyntaxError as e:
    print(f'Ошибка: {e}')
