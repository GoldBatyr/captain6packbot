import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

TOKEN = "8222684433:AAGl7T3wcl3ix-K-yaLcHLtkWOeWZd4EaUA"

logging.basicConfig(level=logging.INFO)

QUESTIONS = [
    {
        "en_q": "INLAND ONLY. Your vessel is meeting another vessel head to head. To comply with the steering and sailing rules, you should:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Ваше судно встречается с другим судном нос к носу. Согласно правилам маневрирования, вы должны:",
        "en_options": ["A) Sound the danger signal", "B) Sound one prolonged and two short blasts", "C) Exchange two short blasts", "D) Exchange one short blast"],
        "ru_options": ["A) Подать сигнал опасности", "B) Подать один продолжительный и два коротких сигнала", "C) Обменяться двумя короткими сигналами", "D) Обменяться одним коротким сигналом"],
        "correct": 3,
        "en_explain": "On inland waters, vessels meeting head-on exchange one short blast and pass port-to-port (starboard helm).",
        "ru_explain": "На внутренних водах при встрече нос к носу суда обмениваются одним коротким сигналом и расходятся правыми бортами."
    },
    {
        "en_q": "INLAND ONLY. What is the whistle signal used to indicate a power-driven vessel leaving a dock?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Какой звуковой сигнал подаёт моторное судно при отходе от причала?",
        "en_options": ["A) One short blast", "B) Three short blasts", "C) One prolonged blast", "D) Three prolonged blasts"],
        "ru_options": ["A) Один короткий сигнал", "B) Три коротких сигнала", "C) Один продолжительный сигнал", "D) Три продолжительных сигнала"],
        "correct": 2,
        "en_explain": "A power-driven vessel leaving a dock sounds one prolonged blast (4-6 seconds) to warn other vessels.",
        "ru_explain": "Судно, отходящее от причала, подаёт один продолжительный сигнал (4–6 секунд) для предупреждения других судов."
    },
    {
        "en_q": "INLAND ONLY. You are overtaking another power-driven vessel in a narrow channel, and you wish to overtake on the other vessel's port side. You will sound:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы обгоняете другое судно в узком канале и хотите обогнать его с левого борта. Вы подаёте:",
        "en_options": ["A) One short blast", "B) Two short blasts", "C) Two prolonged blasts followed by one short blast", "D) Two prolonged blasts followed by two short blasts"],
        "ru_options": ["A) Один короткий сигнал", "B) Два коротких сигнала", "C) Два продолжительных и один короткий сигнал", "D) Два продолжительных и два коротких сигнала"],
        "correct": 1,
        "en_explain": "On inland waters, overtaking on the port side requires two short blasts. The overtaken vessel must respond with the same signal to confirm.",
        "ru_explain": "На внутренних водах при обгоне с левого борта подаётся два коротких сигнала. Обгоняемое судно отвечает тем же сигналом, подтверждая согласие."
    },
    {
        "en_q": "INLAND ONLY. You are crossing the course of another vessel to your starboard. You agreed by radiotelephone to pass astern of her. You MUST:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы пересекаете курс судна справа. По радио договорились пройти за его кормой. Вы ОБЯЗАНЫ:",
        "en_options": ["A) Sound one short blast", "B) Sound two short blasts", "C) Change course to starboard", "D) None of the above"],
        "ru_options": ["A) Подать один короткий сигнал", "B) Подать два коротких сигнала", "C) Изменить курс вправо", "D) Ничего из вышеперечисленного"],
        "correct": 3,
        "en_explain": "If vessels agree to pass by radiotelephone, no additional whistle signals are required. Radio agreement is sufficient under Inland Rule 34(h).",
        "ru_explain": "Если суда договорились о расхождении по радио, дополнительных звуковых сигналов не требуется. Соглашение по радио достаточно согласно правилу 34(h)."
    },
    {
        "en_q": "INLAND ONLY. You are overtaking a vessel in a narrow channel and wish to leave her on your starboard side. You may:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы обгоняете судно в узком канале и хотите оставить его слева. Вы можете:",
        "en_options": ["A) Contact her by radiotelephone to arrange the passage", "B) Overtake without sounding whistle signals", "C) Sound five short blasts", "D) All of the above"],
        "ru_options": ["A) Связаться по радиотелефону для согласования манёвра", "B) Обогнать без звуковых сигналов", "C) Подать пять коротких сигналов", "D) Всё из вышеперечисленного"],
        "correct": 0,
        "en_explain": "Overtaking on the starboard side (non-standard) requires radio agreement. No whistle signals are defined for this maneuver under Inland Rules.",
        "ru_explain": "Обгон с правого борта — нестандартный манёвр, требующий согласования по радио. Звуковые сигналы для этого случая правилами не предусмотрены."
    },
    {
        "en_q": "You are in the middle of a channel. Another vessel is crossing your course from starboard to port, and you are in doubt as to her intentions. You:",
        "ru_q": "Вы на середине канала. Другое судно пересекает ваш курс справа налево, и вы сомневаетесь в его намерениях. Вы:",
        "en_options": ["A) Must sound the danger signal", "B) Are required to back down", "C) May sound the danger signal", "D) Should sound one short blast"],
        "ru_options": ["A) Обязаны подать сигнал опасности", "B) Обязаны дать задний ход", "C) Можете подать сигнал опасности", "D) Должны подать один короткий сигнал"],
        "correct": 0,
        "en_explain": "Under Rule 34(d), when in doubt about another vessel's intentions, you MUST sound the danger signal (5+ short blasts). It is mandatory, not optional.",
        "ru_explain": "По правилу 34(d) при сомнении в намерениях другого судна вы ОБЯЗАНЫ подать сигнал опасности — не менее пяти коротких сигналов. Это обязательно."
    },
    {
        "en_q": "INLAND ONLY. Maneuvering signals shall be sounded on inland waters by:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Манёвренные звуковые сигналы на внутренних водах подаются:",
        "en_options": ["A) All vessels when meeting, crossing, or overtaking in sight of one another", "B) All vessels meeting or crossing within half a mile, not in sight", "C) Power-driven vessels overtaking in sight / crossing within half a mile and in sight", "D) Power-driven vessels crossing within half a mile and NOT in sight"],
        "ru_options": ["A) Всеми судами при встрече, пересечении или обгоне в пределах видимости", "B) Всеми судами в пределах полумили вне видимости", "C) Моторными судами при обгоне в пределах видимости / при пересечении в пределах полумили и в пределах видимости", "D) Моторными судами при пересечении в пределах полумили вне видимости"],
        "correct": 2,
        "en_explain": "Maneuvering signals apply only to power-driven vessels. Vessels must be in sight of each other and within half a mile when crossing.",
        "ru_explain": "Манёвренные сигналы обязательны только для моторных судов в пределах видимости. При пересечении курсов — дополнительно в пределах полумили."
    },
    {
        "en_q": "INLAND ONLY. A light used to signal passing intentions must be a(n):",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Огонь для подачи сигналов о намерениях при расхождении должен быть:",
        "en_options": ["A) All-round white or yellow light", "B) All-round yellow light only", "C) All-round white light only", "D) 225° white light only"],
        "ru_options": ["A) Круговым белым или жёлтым огнём", "B) Только круговым жёлтым огнём", "C) Только круговым белым огнём", "D) Только белым огнём с углом 225°"],
        "correct": 0,
        "en_explain": "Inland Rule 34(b) permits an all-round white OR yellow light for signaling passing intentions.",
        "ru_explain": "Правило 34(b) внутренних вод разрешает круговой белый ИЛИ жёлтый огонь для световой сигнализации манёвренных намерений."
    },
    {
        "en_q": "INLAND ONLY. What MAY be used to indicate the presence of a partly submerged object being towed?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Что МОЖЕТ использоваться для обозначения частично погружённого буксируемого объекта?",
        "en_options": ["A) A black cone, apex upward", "B) Two all-round yellow lights at each end of the tow", "C) The beam of a searchlight from the towing vessel shown in the direction of the tow", "D) All of the above"],
        "ru_options": ["A) Чёрный конус вершиной вверх", "B) Два круговых жёлтых огня на каждом конце буксира", "C) Луч прожектора с буксирующего судна в сторону объекта", "D) Всё из вышеперечисленного"],
        "correct": 2,
        "en_explain": "A searchlight from the towing vessel directed at the submerged object is permitted when lights cannot be placed on the object itself.",
        "ru_explain": "Прожектор с буксировщика, направленный на объект, разрешён когда установить огни непосредственно на буксируемом объекте невозможно."
    },
    {
        "en_q": "BOTH INTERNATIONAL & INLAND. While underway in fog, you hear a prolonged blast from another vessel. This signal indicates a:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Следуя в туман, вы слышите один продолжительный сигнал. Это означает:",
        "en_options": ["A) Sailboat underway", "B) Vessel underway, towing", "C) Vessel underway, making way", "D) Vessel being towed"],
        "ru_options": ["A) Парусное судно на ходу", "B) Судно на ходу с буксиром", "C) Моторное судно на ходу, движущееся вперёд", "D) Буксируемое судно"],
        "correct": 2,
        "en_explain": "One prolonged blast every 2 minutes is the fog signal for a power-driven vessel making way. Towing vessel sounds one prolonged + two short blasts.",
        "ru_explain": "Один продолжительный сигнал каждые 2 минуты — туманный сигнал моторного судна, идущего вперёд. Буксировщик подаёт один продолжительный и два коротких."
    },
]
user_state = {}

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📝 Тест / Quiz", callback_data="menu_quiz")],
        [InlineKeyboardButton("📚 Глоссарий / Glossary", callback_data="menu_glossary")],
        [InlineKeyboardButton("🚗 За рулём / Drive Mode", callback_data="menu_drive")],
    ]
    update.message.reply_text(
        "🚢 Добро пожаловать в Captain6PackBot!\n\nВыберите режим / Choose mode:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if user_id not in user_state:
        user_state[user_id] = {"lang": "ru", "q_index": 0}

    state = user_state[user_id]

    if query.data == "menu_quiz":
        state["q_index"] = 0
        send_question(query, state)
    elif query.data == "toggle_lang":
        state["lang"] = "en" if state["lang"] == "ru" else "ru"
        send_question(query, state)
    elif query.data.startswith("answer_"):
        chosen = int(query.data.split("_")[1])
        q = QUESTIONS[state["q_index"]]
        explain = q["ru_explain"] if state["lang"] == "ru" else q["en_explain"]
        if chosen == q["correct"]:
            result = "✅ Правильно! / Correct!\n\n" + explain
        else:
            result = "❌ Неверно / Wrong!\n\n" + explain
        keyboard = [[InlineKeyboardButton("➡️ Следующий / Next", callback_data="next_question")]]
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "next_question":
        state["q_index"] = (state["q_index"] + 1) % len(QUESTIONS)
        send_question(query, state)
    elif query.data == "menu_glossary":
        query.edit_message_text("📚 Глоссарий в разработке / Glossary coming soon!")
    elif query.data == "menu_drive":
        query.edit_message_text("🚗 Режим за рулём в разработке / Drive mode coming soon!")

def send_question(query, state):
    q = QUESTIONS[state["q_index"]]
    lang = state["lang"]
    question = q["ru_q"] if lang == "ru" else q["en_q"]
    options = q["ru_options"] if lang == "ru" else q["en_options"]
    lang_btn = "🇺🇸 Switch to English" if lang == "ru" else "🇷🇺 Переключить на русский"
    keyboard = []
    for i, opt in enumerate(options):
        keyboard.append([InlineKeyboardButton(opt, callback_data=f"answer_{i}")])
    keyboard.append([InlineKeyboardButton(lang_btn, callback_data="toggle_lang")])
    query.edit_message_text(
        f"❓ Вопрос {state['q_index']+1}\n\n{question}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
