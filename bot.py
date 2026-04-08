import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

TOKEN = "8222684433:AAGl7T3wcl3ix-K-yaLcHLtkWOeWZd4EaUA"

logging.basicConfig(level=logging.INFO)

GLOSSARY = [
    {
        "term": "Port",
        "ru": "Levyj bort",
        "file_id": "CQACAgIAAxkBAAMdadW4TGAhwHmzRyXnJbqSv6ewVBIAAnqeAAIXELFKZX9-mXLEUkU7BA"
    },
    {
        "term": "Starboard",
        "ru": "Pravyj bort",
        "file_id": "CQACAgIAAxkBAAMbadW4TDgWnvdPf7qq_scWI_yFRCYAanieAAIXELFK3uGIBiPuSII7BA"
    },
    {
        "term": "Underway",
        "ru": "Na hodu",
        "file_id": "CQACAgIAAxkBAAMeadW4TCirSAABQzFKQNCrorYwPCkXAAJ7ngACFxCxSpL8H-CBi_BbOwQ"
    },
    {
        "term": "Overtaking",
        "ru": "Obgon",
        "file_id": "CQACAgIAAxkBAAMZadW4TIR3oU6eb7cE-mpWYAI66DkAAnaeAAIXELFKX4lLnsLEOug7BA"
    },
    {
        "term": "Stand-on vessel",
        "ru": "Privilegirovannoe sudno",
        "file_id": "CQACAgIAAxkBAAMcadW4TNDISQVB_rkXQg18rBXIs10AAnmeAAIXELFKWToEjKf_myY7BA"
    },
    {
        "term": "Give-way vessel",
        "ru": "Ustupayushee sudno",
        "file_id": "CQACAgIAAxkBAAMfadW4TD_GyIjTekzxb5SXQYE-ZRwAAnyeAAIXELFKIMD_bOWOVTE7BA"
    },
    {
        "term": "Rules of the Road",
        "ru": "Pravila plavaniya",
        "file_id": "CQACAgIAAxkBAAMaadW4TGT9JISiKDuFDptjii8tCGsAAneeAAIXELFKiytUC_no1GE7BA"
    },
]

QUESTIONS = [
    {
        "en_q": "INLAND ONLY. Your vessel is meeting another vessel head to head. To comply with the steering and sailing rules, you should:",
        "ru_q": "ONLY INLAND. Your vessel meets another vessel head-on. According to maneuvering rules, you should:",
        "en_options": ["A) Sound the danger signal", "B) Sound one prolonged and two short blasts", "C) Exchange two short blasts", "D) Exchange one short blast"],
        "ru_options": ["A) Sound danger signal", "B) One prolonged and two short", "C) Exchange two short", "D) Exchange one short"],
        "correct": 3,
        "en_explain": "Inland Rule 34: vessels meeting head-on exchange ONE short blast, each vessel turns right and passes port-to-port.",
        "ru_explain": "Rule 34: vessels exchange ONE short blast, each turns right and passes port-to-port."
    },
    {
        "en_q": "INLAND ONLY. What is the whistle signal for a power-driven vessel leaving a dock?",
        "ru_q": "ONLY INLAND. What signal does a motor vessel give when leaving a dock?",
        "en_options": ["A) One short blast", "B) Three short blasts", "C) One prolonged blast", "D) Three prolonged blasts"],
        "ru_options": ["A) One short", "B) Three short", "C) One prolonged", "D) Three prolonged"],
        "correct": 2,
        "en_explain": "Inland Rules: a vessel leaving a dock sounds ONE prolonged blast (4-6 sec) to warn nearby vessels.",
        "ru_explain": "Inland Rules: vessel leaving dock sounds ONE prolonged blast (4-6 sec)."
    },
    {
        "en_q": "INLAND ONLY. You are overtaking a vessel in a narrow channel and wish to overtake on her PORT side. You sound:",
        "ru_q": "ONLY INLAND. You are overtaking a vessel in a narrow channel on her PORT side. You sound:",
        "en_options": ["A) One short blast", "B) Two short blasts", "C) Two prolonged + one short", "D) Two prolonged + two short"],
        "ru_options": ["A) One short", "B) Two short", "C) Two prolonged + one short", "D) Two prolonged + two short"],
        "correct": 1,
        "en_explain": "Inland Rule 34: overtaking on PORT side = TWO short blasts. Overtaken vessel responds with same signal.",
        "ru_explain": "Rule 34: overtaking on PORT side = TWO short blasts. Overtaken vessel responds same."
    },
    {
        "en_q": "INLAND ONLY. You agreed by radio to pass ASTERN of a vessel on your starboard. You MUST:",
        "ru_q": "ONLY INLAND. You agreed by radio to pass astern of vessel on starboard. You MUST:",
        "en_options": ["A) Sound one short blast", "B) Sound two short blasts", "C) Change course to starboard", "D) None of the above"],
        "ru_options": ["A) One short blast", "B) Two short blasts", "C) Change course to starboard", "D) None of the above"],
        "correct": 3,
        "en_explain": "Inland Rule 34(h): agreement by radiotelephone is sufficient. No additional whistle signals required.",
        "ru_explain": "Rule 34(h): radio agreement is sufficient. No additional whistle signals required."
    },
    {
        "en_q": "INLAND ONLY. You are overtaking a vessel in a narrow channel and wish to pass on her STARBOARD side. You may:",
        "ru_q": "ONLY INLAND. You are overtaking a vessel and wish to pass on her STARBOARD side. You may:",
        "en_options": ["A) Contact her by radio to arrange passage", "B) Overtake without whistle signals", "C) Sound five short blasts", "D) All of the above"],
        "ru_options": ["A) Contact by radio to arrange passage", "B) Overtake without signals", "C) Sound five short blasts", "D) All of the above"],
        "correct": 0,
        "en_explain": "Inland Rules: overtaking on STARBOARD side is non-standard. Only permitted after radio agreement.",
        "ru_explain": "Overtaking on STARBOARD side is non-standard. Only permitted after radio agreement."
    },
    {
        "en_q": "Another vessel is crossing your course starboard to port and you doubt her intentions. You:",
        "ru_q": "Another vessel crosses your course starboard to port and you doubt her intentions. You:",
        "en_options": ["A) Must sound the danger signal", "B) Must back down", "C) May sound the danger signal", "D) Sound one short blast"],
        "ru_options": ["A) Must sound danger signal", "B) Must back down", "C) May sound danger signal", "D) Sound one short blast"],
        "correct": 0,
        "en_explain": "Rule 34(d): in doubt about another vessel's intentions - MUST sound danger signal (5+ short blasts). Mandatory.",
        "ru_explain": "Rule 34(d): in doubt - MUST sound danger signal (5+ short blasts). Mandatory."
    },
    {
        "en_q": "INLAND ONLY. Maneuvering signals on inland waters are sounded by:",
        "ru_q": "ONLY INLAND. Maneuvering signals on inland waters are sounded by:",
        "en_options": ["A) All vessels meeting/crossing/overtaking in sight", "B) All vessels within half a mile, not in sight", "C) Power-driven vessels overtaking in sight / crossing within half a mile in sight", "D) Power-driven vessels crossing within half a mile, NOT in sight"],
        "ru_options": ["A) All vessels meeting/crossing/overtaking in sight", "B) All vessels within half mile, not in sight", "C) Power-driven: overtaking in sight / crossing within half mile in sight", "D) Power-driven: crossing within half mile, NOT in sight"],
        "correct": 2,
        "en_explain": "Inland Rules: maneuvering signals for power-driven vessels only, in sight. Crossing: also within half a mile.",
        "ru_explain": "Maneuvering signals for power-driven vessels only, in sight. Crossing: also within half a mile."
    },
    {
        "en_q": "INLAND ONLY. A light used to signal passing intentions must be:",
        "ru_q": "ONLY INLAND. A light used to signal passing intentions must be:",
        "en_options": ["A) All-round white OR yellow", "B) All-round yellow only", "C) All-round white only", "D) 225 degree white only"],
        "ru_options": ["A) All-round white OR yellow", "B) All-round yellow only", "C) All-round white only", "D) 225 degree white only"],
        "correct": 0,
        "en_explain": "Inland Rule 34(b): all-round white OR yellow light permitted for signaling passing intentions.",
        "ru_explain": "Rule 34(b): all-round white OR yellow light permitted."
    },
    {
        "en_q": "INLAND ONLY. What MAY indicate a partly submerged object being towed?",
        "ru_q": "ONLY INLAND. What MAY indicate a partly submerged object being towed?",
        "en_options": ["A) Black cone, apex up", "B) Two all-round yellow lights at each end", "C) Searchlight from towing vessel aimed at the tow", "D) All of the above"],
        "ru_options": ["A) Black cone apex up", "B) Two all-round yellow lights each end", "C) Searchlight from towing vessel at tow", "D) All of the above"],
        "correct": 2,
        "en_explain": "Inland Rules: searchlight from towing vessel aimed at tow permitted when lights cannot be mounted on object.",
        "ru_explain": "Searchlight from towing vessel permitted when lights cannot be mounted on object."
    },
    {
        "en_q": "BOTH INT & INLAND. Underway in fog, you hear ONE prolonged blast. This indicates:",
        "ru_q": "BOTH INT & INLAND. In fog you hear ONE prolonged blast. This indicates:",
        "en_options": ["A) Sailboat underway", "B) Vessel towing", "C) Power vessel making way", "D) Vessel being towed"],
        "ru_options": ["A) Sailboat underway", "B) Vessel towing", "C) Power vessel making way", "D) Vessel being towed"],
        "correct": 2,
        "en_explain": "Rule 35: ONE prolonged blast every 2 min = power-driven vessel making way. Towing: one prolonged + two short.",
        "ru_explain": "Rule 35: ONE prolonged every 2 min = power vessel making way. Towing: one prolonged + two short."
    },
]

user_state = {}

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Quiz", callback_data="menu_quiz")],
        [InlineKeyboardButton("Glossary", callback_data="menu_glossary")],
        [InlineKeyboardButton("Drive Mode", callback_data="menu_drive")],
    ]
    update.message.reply_text(
        "Welcome to Captain6PackBot!\n\nChoose mode:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def send_glossary(chat_id, context, index, message_to_delete=None):
    term = GLOSSARY[index]
    caption = f"Glossary {index + 1} of {len(GLOSSARY)}\n\nEN: {term['term']}\nRU: {term['ru']}"
    prev_index = (index - 1) % len(GLOSSARY)
    keyboard = [
        [InlineKeyboardButton("<< Prev", callback_data=f"glo{prev_index}")],
        [InlineKeyboardButton("Menu", callback_data="main_menu")],
    ]
    if message_to_delete:
        try:
            message_to_delete.delete()
        except Exception:
            pass
    context.bot.send_audio(
        chat_id=chat_id,
        audio=term["file_id"],
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def send_question(query, state):
    q = QUESTIONS[state["q_index"]]
    lang = state["lang"]
    question = q["ru_q"] if lang == "ru" else q["en_q"]
    options = q["ru_options"] if lang == "ru" else q["en_options"]
    lang_btn = "Switch to RU" if lang == "en" else "Switch to EN"
    options_text = "\n".join(options)
    full_text = f"Question {state['q_index'] + 1} of {len(QUESTIONS)}\n\n{question}\n\n{options_text}"
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
        send_glossary(query.message.chat_id, context, 0, query.message)

    elif query.data.startswith("glo"):
        index = int(query.data[3:])
        state["g_index"] = index
        send_glossary(query.message.chat_id, context, index, query.message)

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("Quiz", callback_data="menu_quiz")],
            [InlineKeyboardButton("Glossary", callback_data="menu_glossary")],
            [InlineKeyboardButton("Drive Mode", callback_data="menu_drive")],
        ]
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Welcome to Captain6PackBot!\n\nChoose mode:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "toggle_lang":
        state["lang"] = "en" if state["lang"] == "ru" else "ru"
        send_question(query, state)

    elif query.data.startswith("answer_"):
        chosen = int(query.data.split("_")[1])
        q = QUESTIONS[state["q_index"]]
        explain = q["ru_explain"] if state["lang"] == "ru" else q["en_explain"]
        correct_letter = ["A", "B", "C", "D"][q["correct"]]
        if chosen == q["correct"]:
            result = f"Correct!\n\n{explain}"
        else:
            chosen_letter = ["A", "B", "C", "D"][chosen]
            result = f"Wrong! You chose {chosen_letter}, correct answer: {correct_letter}\n\n{explain}"
        keyboard = [[InlineKeyboardButton("Next >>", callback_data="next_question")]]
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "next_question":
        state["q_index"] = (state["q_index"] + 1) % len(QUESTIONS)
        send_question(query, state)

    elif query.data == "menu_drive":
        query.edit_message_text("Drive mode coming soon!")

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
