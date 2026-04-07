import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

TOKEN = "8222684433:AAGl7T3wcl3ix-K-yaLcHLtkWOeWZd4EaUA"

logging.basicConfig(level=logging.INFO)

QUESTIONS = [
    {
        "en_q": "What does 'starboard' mean?",
        "ru_q": "Что означает слово 'starboard'?",
        "en_options": ["A) Left side", "B) Right side", "C) Front", "D) Back"],
        "ru_options": ["A) Левый борт", "B) Правый борт", "C) Нос", "D) Корма"],
        "correct": 1,
        "en_explain": "Starboard is the RIGHT side.",
        "ru_explain": "Starboard — это ПРАВЫЙ борт."
    },
    {
        "en_q": "What color is the starboard light?",
        "ru_q": "Какого цвета огонь правого борта?",
        "en_options": ["A) Red", "B) White", "C) Green", "D) Yellow"],
        "ru_options": ["A) Красный", "B) Белый", "C) Зелёный", "D) Жёлтый"],
        "correct": 2,
        "en_explain": "Starboard light is GREEN.",
        "ru_explain": "Огонь правого борта — ЗЕЛЁНЫЙ."
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
