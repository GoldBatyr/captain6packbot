import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8222684433:AAGl7T3wcl3ix-K-yaLcHLtkWOeWZd4EaUA"

logging.basicConfig(level=logging.INFO)

QUESTIONS = [
    {
        "en_q": "What does 'starboard' mean?",
        "ru_q": "Что означает слово 'starboard'?",
        "en_options": ["A) Left side of the boat", "B) Right side of the boat", "C) Front of the boat", "D) Back of the boat"],
        "ru_options": ["A) Левая сторона судна", "B) Правая сторона судна", "C) Нос судна", "D) Корма судна"],
        "correct": 1,
        "en_explain": "Starboard is always the RIGHT side of the vessel.",
        "ru_explain": "Starboard — это всегда ПРАВЫЙ борт судна."
    },
    {
        "en_q": "What color is the starboard navigation light?",
        "ru_q": "Какого цвета навигационный огонь правого борта?",
        "en_options": ["A) Red", "B) White", "C) Green", "D) Yellow"],
        "ru_options": ["A) Красный", "B) Белый", "C) Зелёный", "D) Жёлтый"],
        "correct": 2,
        "en_explain": "Starboard (right) navigation light is GREEN.",
        "ru_explain": "Навигационный огонь правого борта (starboard) — ЗЕЛЁНЫЙ."
    },
]

user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Тест / Quiz", callback_data="menu_quiz")],
        [InlineKeyboardButton("📚 Глоссарий / Glossary", callback_data="menu_glossary")],
        [InlineKeyboardButton("🚗 За рулём / Drive Mode", callback_data="menu_drive")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🚢 Добро пожаловать в Captain6PackBot!\nWelcome to Captain6PackBot!\n\nВыберите режим / Choose mode:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_state:
        user_state[user_id] = {"lang": "ru", "q_index": 0}

    state = user_state[user_id]

    if query.data == "menu_quiz":
        state["q_index"] = 0
        await send_question(query, state)

    elif query.data == "toggle_lang":
        state["lang"] = "en" if state["lang"] == "ru" else "ru"
        await send_question(query, state)

    elif query.data.startswith("answer_"):
        chosen = int(query.data.split("_")[1])
        q = QUESTIONS[state["q_index"]]
        correct = q["correct"]
        explain = q["ru_explain"] if state["lang"] == "ru" else q["en_explain"]

        if chosen == correct:
            result = "✅ Правильно! / Correct!\n\n" + explain
        else:
            result = "❌ Неверно / Wrong!\n\n" + explain

        keyboard = [[InlineKeyboardButton("➡️ Следующий / Next", callback_data="next_question")]]
        await query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "next_question":
        state["q_index"] = (state["q_index"] + 1) % len(QUESTIONS)
        await send_question(query, state)

    elif query.data == "menu_glossary":
        await query.edit_message_text("📚 Глоссарий в разработке / Glossary coming soon!")

    elif query.data == "menu_drive":
        await query.edit_message_text("🚗 Режим за рулём в разработке / Drive mode coming soon!")

async def send_question(query, state):
    q = QUESTIONS[state["q_index"]]
    lang = state["lang"]
    question = q["ru_q"] if lang == "ru" else q["en_q"]
    options = q["ru_options"] if lang == "ru" else q["en_options"]
    lang_btn = "🇺🇸 Switch to English" if lang == "ru" else "🇷🇺 Переключить на русский"

    keyboard = []
    for i, opt in enumerate(options):
        keyboard.append([InlineKeyboardButton(opt, callback_data=f"answer_{i}")])
    keyboard.append([InlineKeyboardButton(lang_btn, callback_data="toggle_lang")])

    await query.edit_message_text(
        f"❓ Вопрос {state['q_index']+1} / Question {state['q_index']+1}\n\n{question}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
