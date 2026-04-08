import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

TOKEN = "8222684433:AAGl7T3wcl3ix-K-yaLcHLtkWOeWZd4EaUA"

logging.basicConfig(level=logging.INFO)

GLOSSARY = [
    {
        "term": "Port",
        "ru": "Левый борт",
        "file_id": "CQACAgIAAxkBAAMdadW4TGAhwHmzRyXnJbqSv6ewVBIAAnqeAAIXELFKZX9-mXLEUkU7BA"
    },
    {
        "term": "Starboard",
        "ru": "Правый борт",
        "file_id": "CQACAgIAAxkBAAMbadW4TDgWnvdPf7qq_scWI_yFRCYAanieAAIXELFK3uGIBiPuSII7BA"
    },
    {
        "term": "Underway",
        "ru": "На ходу",
        "file_id": "CQACAgIAAxkBAAMeadW4TCirSAABQzFKQNCrorYwPCkXAAJ7ngACFxCxSpL8H-CBi_BbOwQ"
    },
    {
        "term": "Overtaking",
        "ru": "Обгон",
        "file_id": "CQACAgIAAxkBAAMZadW4TIR3oU6eb7cE-mpWYAI66DkAAnaeAAIXELFKX4lLnsLEOug7BA"
    },
    {
        "term": "Stand-on vessel",
        "ru": "Привилегированное судно",
        "file_id": "CQACAgIAAxkBAAMcadW4TNDISQVB_rkXQg18rBXIs10AAnmeAAIXELFKWToEjKf_myY7BA"
    },
    {
        "term": "Give-way vessel",
        "ru": "Уступающее судно",
        "file_id": "CQACAgIAAxkBAAMfadW4TD_GyIjTekzxb5SXQYE-ZRwAAnyeAAIXELFKIMD_bOWOVTE7BA"
    },
    {
        "term": "Rules of the Road",
        "ru": "Правила плавания",
        "file_id": "CQACAgIAAxkBAAMaadW4TGT9JISiKDuFDptjii8tCGsAAneeAAIXELFKiytUC_no1GE7BA"
    },
]

QUESTIONS = [
    {
        "en_q": "INLAND ONLY. Your vessel is meeting another vessel head to head. To comply with the steering and sailing rules, you should:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Ваше судно встречается с другим судном нос к носу. Согласно правилам маневрирования, вы должны:",
        "en_options": ["A) Sound the danger signal", "B) Sound one prolonged and two short blasts", "C) Exchange two short blasts", "D) Exchange one short blast"],
        "ru_options": ["A) Подать сигнал опасности", "B) Один продолжительный и два коротких", "C) Обменяться двумя короткими", "D) Обменяться одним коротким"],
        "correct": 3,
        "en_explain": "Inland Rule 34: vessels meeting head-on exchange ONE short blast, each vessel turns right and passes port-to-port.",
        "ru_explain": "Правило 34: суда обмениваются ОДНИМ коротким сигналом, каждый берёт вправо и расходятся левыми бортами."
    },
    {
        "en_q": "INLAND ONLY. What is the whistle signal for a power-driven vessel leaving a dock?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Какой сигнал подаёт моторное судно при отходе от причала?",
        "en_options": ["A) One short blast", "B) Three short blasts", "C) One prolonged blast", "D) Three prolonged blasts"],
        "ru_options": ["A) Один короткий", "B) Три коротких", "C) Один продолжительный", "D) Три продолжительных"],
        "correct": 2,
        "en_explain": "Inland Rules: a vessel leaving a dock sounds ONE prolonged blast (4-6 sec) to warn nearby vessels.",
        "ru_explain": "Внутренние воды: судно, отходящее от причала, подаёт ОДИН продолжительный сигнал (4-6 сек)."
    },
    {
        "en_q": "INLAND ONLY. You are overtaking a vessel in a narrow channel and wish to overtake on her PORT side. You sound:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы обгоняете судно в узком канале и хотите обогнать его с ЛЕВОГО борта. Вы подаёте:",
        "en_options": ["A) One short blast", "B) Two short blasts", "C) Two prolonged + one short", "D) Two prolonged + two short"],
        "ru_options": ["A) Один короткий", "B) Два коротких", "C) Два продолжительных + один короткий", "D) Два продолжительных + два коротких"],
        "correct": 1,
        "en_explain": "Inland Rule 34: overtaking on PORT side = TWO short blasts. Overtaken vessel responds with same signal to confirm.",
        "ru_explain": "Правило 34: обгон с левого (PORT) борта = ДВА коротких сигнала. Обгоняемое судно отвечает тем же сигналом."
    },
    {
        "en_q": "INLAND ONLY. You agreed by radio to pass ASTERN of a vessel on your starboard. You MUST:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. По радио договорились пройти за кормой судна справа. Вы ОБЯЗАНЫ:",
        "en_options": ["A) Sound one short blast", "B) Sound two short blasts", "C) Change course to starboard", "D) None of the above"],
        "ru_options": ["A) Один короткий сигнал", "B) Два коротких сигнала", "C) Изменить курс вправо", "D) Ничего из вышеперечисленного"],
        "correct": 3,
        "en_explain": "Inland Rule 34(h): agreement by radiotelephone is sufficient. No additional whistle signals required.",
        "ru_explain": "Правило 34(h): соглашение по радио достаточно. Дополнительных звуковых сигналов не требуется."
    },
    {
        "en_q": "INLAND ONLY. You are overtaking a vessel in a narrow channel and wish to pass on her STARBOARD side. You may:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы обгоняете судно в узком канале и хотите обойти его с ПРАВОГО борта. Вы можете:",
        "en_options": ["A) Contact her by radio to arrange passage", "B) Overtake without whistle signals", "C) Sound five short blasts", "D) All of the above"],
        "ru_options": ["A) Связаться по радио для согласования", "B) Обогнать без сигналов", "C) Подать пять коротких", "D) Всё вышеперечисленное"],
        "correct": 0,
        "en_explain": "Inland Rules: overtaking on STARBOARD side is non-standard. Only permitted after radio agreement.",
        "ru_explain": "Обгон с правого борта — нестандартный манёвр. Разрешён только после согласования по радио."
    },
    {
        "en_q": "Another vessel is crossing your course starboard to port and you doubt her intentions. You:",
        "ru_q": "Другое судно пересекает ваш курс справа налево, вы сомневаетесь в его намерениях. Вы:",
        "en_options": ["A) Must sound the danger signal", "B) Must back down", "C) May sound the danger signal", "D) Sound one short blast"],
        "ru_options": ["A) Обязаны подать сигнал опасности", "B) Обязаны дать задний ход", "C) Можете подать сигнал опасности", "D) Подать один короткий"],
        "correct": 0,
        "en_explain": "Rule 34(d): in doubt about another vessel's intentions — MUST sound danger signal (5+ short blasts). Mandatory.",
        "ru_explain": "Правило 34(d): при сомнении в намерениях — ОБЯЗАНЫ подать сигнал опасности (5+ коротких). Обязательно."
    },
    {
        "en_q": "INLAND ONLY. Maneuvering signals on inland waters are sounded by:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Манёвренные сигналы на внутренних водах подаются:",
        "en_options": ["A) All vessels meeting/crossing/overtaking in sight", "B) All vessels within half a mile, not in sight", "C) Power-driven vessels overtaking in sight / crossing within half a mile in sight", "D) Power-driven vessels crossing within half a mile, NOT in sight"],
        "ru_options": ["A) Всеми судами при встрече/пересечении/обгоне в видимости", "B) Всеми судами в пределах полумили вне видимости", "C) Моторными: при обгоне в видимости / пересечении в полумиле и в видимости", "D) Моторными при пересечении в полумиле вне видимости"],
        "correct": 2,
        "en_explain": "Inland Rules: maneuvering signals for power-driven vessels only, in sight of each other. Crossing: also within half a mile.",
        "ru_explain": "Манёвренные сигналы — только для моторных судов в пределах видимости. Пересечение курсов — дополнительно в пределах полумили."
    },
    {
        "en_q": "INLAND ONLY. A light used to signal passing intentions must be:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Огонь для сигнализации намерений при расхождении должен быть:",
        "en_options": ["A) All-round white OR yellow", "B) All-round yellow only", "C) All-round white only", "D) 225° white only"],
        "ru_options": ["A) Круговой белый ИЛИ жёлтый", "B) Только круговой жёлтый", "C) Только круговой белый", "D) Только белый 225°"],
        "correct": 0,
        "en_explain": "Inland Rule 34(b): all-round white OR yellow light permitted for signaling passing intentions.",
        "ru_explain": "Правило 34(b): разрешён круговой белый ИЛИ жёлтый огонь для сигнализации намерений."
    },
    {
        "en_q": "INLAND ONLY. What MAY indicate a partly submerged object being towed?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Что МОЖЕТ обозначать частично погружённый буксируемый объект?",
        "en_options": ["A) Black cone, apex up", "B) Two all-round yellow lights at each end", "C) Searchlight from towing vessel aimed at the tow", "D) All of the above"],
        "ru_options": ["A) Чёрный конус вершиной вверх", "B) Два круговых жёлтых огня на каждом конце", "C) Прожектор с буксировщика на объект", "D) Всё вышеперечисленное"],
        "correct": 2,
        "en_explain": "Inland Rules: searchlight from towing vessel aimed at the tow is permitted when lights cannot be mounted on the object.",
        "ru_explain": "Прожектор с буксировщика допускается когда огни невозможно установить на объекте."
    },
    {
        "en_q": "BOTH INT & INLAND. Underway in fog, you hear ONE prolonged blast. This indicates:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. В тумане слышите ОДИН продолжительный сигнал. Это:",
        "en_options": ["A) Sailboat underway", "B) Vessel towing", "C) Power vessel making way", "D) Vessel being towed"],
        "ru_options": ["A) Парусное судно на ходу", "B) Судно с буксиром", "C) Моторное судно, идущее вперёд", "D) Буксируемое судно"],
        "correct": 2,
        "en_explain": "Rule 35: ONE prolonged blast every 2 min = power-driven vessel making way. Towing: one prolonged + two short.",
        "ru_explain": "Правило 35: ОДИН продолжительный каждые 2 мин = моторное судно идёт вперёд. Буксировщик: один продолжительный + два коротких."
    },
]

user_state = {}

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📝 Тест / Quiz", callback_data="menu_quiz")],
        [InlineKeyboardButton("📖 Глоссарий / Glossary", callback_data="menu_glossary")],
        [InlineKeyboardButton("🚗 За рулём / Drive Mode", callback_data="menu_drive")],
    ]
    update.message.reply_text(
        "⚓ Добро пожаловать в Captain6PackBot!\n\nВыберите режим / Choose mode:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def send_glossary(query, index):
    term = GLOSSARY[index]
    caption = f"📖 {index + 1} из {len(GLOSSARY)}\n\n🇺🇸 {term['term']}\n🇷🇺 {term['ru']}"
    keyboard = [
        [
            InlineKeyboardButton("⬅️", callback_data=f"glossary_{(index - 1) % len(GLOSSARY)}"),
            InlineKeyboardButton("➡️", callback_data=f"glossary_{(index + 1) % len(GLOSSARY)}"),
        ],
        [InlineKeyboardButton("🏠 Меню / Menu", callback_data="main_menu")],
    ]
    try:
        query.message.delete()
    except:
        pass
    query.message.reply_audio(
        audio=term["file_id"],
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def send_question(query, state):
    q = QUESTIONS[state["q_index"]]
    lang = state["lang"]
    question = q["ru_q"] if lang == "ru" else q["en_q"]
    options = q["ru_options"] if lang == "ru" else q["en_options"]
    lang_btn = "🇺🇸 English" if lang == "ru" else "🇷🇺 Русский"
    options_text = "\n".join(options)
    full_text = f"❓ Вопрос {state['q_index'] + 1} из {len(QUESTIONS)}\n\n{question}\n\n{options_text}"
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data="answer_0"),
            InlineKeyboardButton("B", callback_data="answer_1"),
            InlineKeyboardButton("C", callback_data="answer_2"),
            InlineKeyboardButton("D", callback_data="answer_3"),
        ],
        [InlineKeyboardButton(lang_btn, callback_data="toggle_lang")],
    ]
    query.edit_message_text(full_text, reply_markup=InlineKeyboardMarkup(keyboard))

def get_file_id(update: Update, context: CallbackContext):
    if update.message.audio:
        file_id = update.message.audio.file_id
        name = update.message.audio.file_name
        update.message.reply_text(f"{name}:\n{file_id}")
    elif update.message.document:
        file_id = update.message.document.file_id
        name = update.message.document.file_name
        update.message.reply_text(f"{name}:\n{file_id}")

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if user_id not in user_state:
        user_state[user_id] = {"lang": "ru", "q_index": 0, "g_index": 0}

    state = user_state[user_id]

    if query.data == "menu_quiz":
        state["q_index"] = 0
        send_question(query, state)
    elif query.data == "menu_glossary":
        state["g_index"] = 0
        send_glossary(query, 0)
    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📝 Тест / Quiz", callback_data="menu_quiz")],
            [InlineKeyboardButton("📖 Глоссарий / Glossary", callback_data="menu_glossary")],
            [InlineKeyboardButton("🚗 За рулём / Drive Mode", callback_data="menu_drive")],
        ]
        try:
            query.edit_message_text(
                "⚓ Добро пожаловать в Captain6PackBot!\n\nВыберите режим / Choose mode:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            query.message.delete()
            query.message.reply_text(
                "⚓ Добро пожаловать в Captain6PackBot!\n\nВыберите режим / Choose mode:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    elif query.data.startswith("glossary_"):
        index = int(query.data.split("_")[1])
        state["g_index"] = index
        send_glossary(query, index)
    elif query.data == "toggle_lang":
        state["lang"] = "en" if state["lang"] == "ru" else "ru"
        send_question(query, state)
    elif query.data.startswith("answer_"):
        chosen = int(query.data.split("_")[1])
        q = QUESTIONS[state["q_index"]]
        explain = q["ru_explain"] if state["lang"] == "ru" else q["en_explain"]
        correct_letter = ["A", "B", "C", "D"][q["correct"]]
        if chosen == q["correct"]:
            result = f"✅ Правильно! / Correct!\n\n{explain}"
        else:
            chosen_letter = ["A", "B", "C", "D"][chosen]
            result = f"❌ Неверно! Вы выбрали {chosen_letter}, правильный ответ: {correct_letter}\n\n{explain}"
        keyboard = [[InlineKeyboardButton("➡️ Следующий / Next", callback_data="next_question")]]
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "next_question":
        state["q_index"] = (state["q_index"] + 1) % len(QUESTIONS)
        send_question(query, state)
    elif query.data == "menu_drive":
        query.edit_message_text("🚗 Режим за рулём в разработке / Drive mode coming soon!")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.audio | Filters.document, get_file_id))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
