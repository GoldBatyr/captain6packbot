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
        "ru_q": "INLAND ONLY. Vashe sudno vstrechaetsya s drugim sudnom nos k nosu. Soglasno pravilam, vy dolzhny:",
        "en_options": ["A) Sound the danger signal", "B) Sound one prolonged and two short blasts", "C) Exchange two short blasts", "D) Exchange one short blast"],
        "ru_options": ["A) Podat signal opasnosti", "B) Odin prolongirovanny i dva korotkih", "C) Obmenyatsya dvumya korotkimi", "D) Obmenyatsya odnim korotkim"],
        "correct": 3,
        "en_explain": "Inland Rule 34: vessels meeting head-on exchange ONE short blast, each vessel turns right and passes port-to-port.",
        "ru_explain": "Pravilo 34: suda obmenivauytsya ODNIM korotkim signalom, kazhdyj beryot vpravo i raskhodyatsya levymi bortami."
    },
    {
        "en_q": "INLAND ONLY. What is the whistle signal for a power-driven vessel leaving a dock?",
        "ru_q": "INLAND ONLY. Kakoj signal podayet motornoe sudno pri otkhode ot prichala?",
        "en_options": ["A) One short blast", "B) Three short blasts", "C) One prolonged blast", "D) Three prolonged blasts"],
        "ru_options": ["A) Odin korotkij", "B) Tri korotkih", "C) Odin prolongirovanny", "D) Tri prolongirovannykh"],
        "correct": 2,
        "en_explain": "Inland Rules: a vessel leaving a dock sounds ONE prolonged blast (4-6 sec) to warn nearby vessels.",
        "ru_explain": "Vnutrennie vody: sudno otkhodyashee ot prichala podayet ODIN prolongirovanny signal (4-6 sek)."
    },
    {
        "en_q": "INLAND ONLY. You are overtaking a vessel in a narrow channel and wish to overtake on her PORT side. You sound:",
        "ru_q": "INLAND ONLY. Vy obgonyaete sudno v uzkom kanale i khotite obognat ego s LEVOGO borta. Vy podayote:",
        "en_options": ["A) One short blast", "B) Two short blasts", "C) Two prolonged + one short", "D) Two prolonged + two short"],
        "ru_options": ["A) Odin korotkij", "B) Dva korotkih", "C) Dva prolongirovannykh + odin korotkij", "D) Dva prolongirovannykh + dva korotkih"],
        "correct": 1,
        "en_explain": "Inland Rule 34: overtaking on PORT side = TWO short blasts. Overtaken vessel responds with same signal.",
        "ru_explain": "Pravilo 34: obgon s levogo (PORT) borta = DVA korotkih signala. Obgonyaemoe sudno otvechaet tem zhe signalom."
    },
    {
        "en_q": "INLAND ONLY. You agreed by radio to pass ASTERN of a vessel on your starboard. You MUST:",
        "ru_q": "INLAND ONLY. Po radio dogovorilis projti za kormoj sudna sprava. Vy OBYAZANY:",
        "en_options": ["A) Sound one short blast", "B) Sound two short blasts", "C) Change course to starboard", "D) None of the above"],
        "ru_options": ["A) Odin korotkij signal", "B) Dva korotkih signala", "C) Izmenit kurs vpravo", "D) Nichego iz vyssheperechislennogo"],
        "correct": 3,
        "en_explain": "Inland Rule 34(h): agreement by radiotelephone is sufficient. No additional whistle signals required.",
        "ru_explain": "Pravilo 34(h): soglashenie po radio dostatochno. Dopolnitelnykh zvukovykh signalov ne trebuetsya."
    },
    {
        "en_q": "INLAND ONLY. You are overtaking a vessel in a narrow channel and wish to pass on her STARBOARD side. You may:",
        "ru_q": "INLAND ONLY. Vy obgonyaete sudno v uzkom kanale i khotite obojti ego s PRAVOGO borta. Vy mozhete:",
        "en_options": ["A) Contact her by radio to arrange passage", "B) Overtake without whistle signals", "C) Sound five short blasts", "D) All of the above"],
        "ru_options": ["A) Svyazatsya po radio dlya soglasovaniya", "B) Obognat bez signalov", "C) Podat pyat korotkih", "D) Vsyo iz vyssheperechislennogo"],
        "correct": 0,
        "en_explain": "Inland Rules: overtaking on STARBOARD side is non-standard. Only permitted after radio agreement.",
        "ru_explain": "Obgon s pravogo borta - nestandartny manyovr. Razreshen tolko posle soglasovaniya po radio."
    },
    {
        "en_q": "Another vessel is crossing your course starboard to port and you doubt her intentions. You:",
        "ru_q": "Drugoe sudno peresekaet vash kurs sprava nalevo, vy somnevayetes v ego namereniyakh. Vy:",
        "en_options": ["A) Must sound the danger signal", "B) Must back down", "C) May sound the danger signal", "D) Sound one short blast"],
        "ru_options": ["A) Obyazany podat signal opasnosti", "B) Obyazany dat zadnij khod", "C) Mozhete podat signal opasnosti", "D) Podat odin korotkij"],
        "correct": 0,
        "en_explain": "Rule 34(d): in doubt about another vessel's intentions - MUST sound danger signal (5+ short blasts). Mandatory.",
        "ru_explain": "Pravilo 34(d): pri somnenii v namereniyakh - OBYAZANY podat signal opasnosti (5+ korotkih). Obyazatelno."
    },
    {
        "en_q": "INLAND ONLY. Maneuvering signals on inland waters are sounded by:",
        "ru_q": "INLAND ONLY. Manyovrennye signaly na vnutrennikh vodakh podayutsya:",
        "en_options": ["A) All vessels meeting/crossing/overtaking in sight", "B) All vessels within half a mile, not in sight", "C) Power-driven vessels overtaking in sight / crossing within half a mile in sight", "D) Power-driven vessels crossing within half a mile, NOT in sight"],
        "ru_options": ["A) Vsemi sudami pri vstreche/peresechenii/obgone v vidimosti", "B) Vsemi sudami v predelakh polumili vne vidimosti", "C) Motornymi: obgon v vidimosti / peresechenie v polumile i v vidimosti", "D) Motornymi pri peresechenii v polumile vne vidimosti"],
        "correct": 2,
        "en_explain": "Inland Rules: maneuvering signals for power-driven vessels only, in sight. Crossing: also within half a mile.",
        "ru_explain": "Manyovrennye signaly - tolko dlya motornykh sudov v predelakh vidimosti. Peresechenie kursov - dopolnitelno v predelakh polumili."
    },
    {
        "en_q": "INLAND ONLY. A light used to signal passing intentions must be:",
        "ru_q": "INLAND ONLY. Ogon dlya signalizatsii namerenij pri raskhozdenii dolzhen byt:",
        "en_options": ["A) All-round white OR yellow", "B) All-round yellow only", "C) All-round white only", "D) 225 degree white only"],
        "ru_options": ["A) Krugovoj belyj ILI zholtyj", "B) Tolko krugovoj zholtyj", "C) Tolko krugovoj belyj", "D) Tolko belyj 225 gradusov"],
        "correct": 0,
        "en_explain": "Inland Rule 34(b): all-round white OR yellow light permitted for signaling passing intentions.",
        "ru_explain": "Pravilo 34(b): razreshen krugovoj belyj ILI zholtyj ogon dlya signalizatsii namerenij."
    },
    {
        "en_q": "INLAND ONLY. What MAY indicate a partly submerged object being towed?",
        "ru_q": "INLAND ONLY. Chto MOZHET oboznachat chastichno pogruzhennyj buksiruemyj obekt?",
        "en_options": ["A) Black cone, apex up", "B) Two all-round yellow lights at each end", "C) Searchlight from towing vessel aimed at the tow", "D) All of the above"],
        "ru_options": ["A) Chernyj konus vershinoj vverkh", "B) Dva krugovykh zholtykh ognya na kazhdom kontse", "C) Prozhektor s buksirovshhika na obekt", "D) Vsyo iz vyssheperechislennogo"],
        "correct": 2,
        "en_explain": "Inland Rules: searchlight from towing vessel aimed at tow permitted when lights cannot be mounted on object.",
        "ru_explain": "Prozhektor s buksirovshhika dopuskaetsya kogda ogni nevozmozhno ustanovit na obekte."
    },
    {
        "en_q": "BOTH INT & INLAND. Underway in fog, you hear ONE prolonged blast. This indicates:",
        "ru_q": "BOTH INT & INLAND. V tumane slyshite ODIN prolongirovanny signal. Eto:",
        "en_options": ["A) Sailboat underway", "B) Vessel towing", "C) Power vessel making way", "D) Vessel being towed"],
        "ru_options": ["A) Parusnoe sudno na khodu", "B) Sudno s buksirom", "C) Motornoe sudno idushee vperyod", "D) Buksiruemoe sudno"],
        "correct": 2,
        "en_explain": "Rule 35: ONE prolonged blast every 2 min = power-driven vessel making way. Towing: one prolonged + two short.",
        "ru_explain": "Pravilo 35: ODIN prolongirovanny kazhdye 2 min = motornoe sudno idyot vperyod. Buksirovshhik: odin prolongirovanny + dva korotkih."
    },
]

user_state = {}

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Test / Quiz", callback_data="menu_quiz")],
        [InlineKeyboardButton("Glossarij / Glossary", callback_data="menu_glossary")],
        [InlineKeyboardButton("Za rulyom / Drive Mode", callback_data="menu_drive")],
    ]
    update.message.reply_text(
        "Dobro pozhalovat v Captain6PackBot!\n\nVyberite rezhim / Choose mode:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def send_glossary(chat_id, context, index, message_to_delete=None):
    term = GLOSSARY[index]
    caption = f"Glossarij {index + 1} iz {len(GLOSSARY)}\n\nEN: {term['term']}\nRU: {term['ru']}"
    prev_index = (index - 1) % len(GLOSSARY)
    keyboard = [
        [InlineKeyboardButton("<< Nazad / Back", callback_data=f"glo{prev_index}")],
        [InlineKeyboardButton("Menyu / Menu", callback_data="main_menu")],
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
    lang_btn = "Switch to English" if lang == "ru" else "Switch to Russian"
    options_text = "\n".join(options)
    full_text = f"Vopros {state['q_index'] + 1} iz {len(QUESTIONS)}\n\n{question}\n\n{options_text}"
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
            [InlineKeyboardButton("Test / Quiz", callback_data="menu_quiz")],
            [InlineKeyboardButton("Glossarij / Glossary", callback_data="menu_glossary")],
            [InlineKeyboardButton("Za rulyom / Drive Mode", callback_data="menu_drive")],
        ]
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Dobro pozhalovat v Captain6PackBot!\n\nVyberite rezhim / Choose mode:",
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
            result = f"Pravilno! / Correct!\n\n{explain}"
        else:
            chosen_letter = ["A", "B", "C", "D"][chosen]
            result = f"Neverno! Vy vybrali {chosen_letter}, pravilnyj otvet: {correct_letter}\n\n{explain}"
        keyboard = [[InlineKeyboardButton("Sleduyushij / Next >>", callback_data="next_question")]]
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "next_question":
        state["q_index"] = (state["q_index"] + 1) % len(QUESTIONS)
        send_question(query, state)

    elif query.data == "menu_drive":
        query.edit_message_text("Rezhim za rulyom v razrabotke / Drive mode coming soon!")

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
