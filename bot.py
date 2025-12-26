from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import time
import re

TOKEN = "8399873866:AAF-K9_6ytC6Y6l4tbWEuxhY-U3xNToLDEo"

RULES_TEXT = """
🗓 Правила чата

1. Будьте вежливы 🚫
2. Не используйте мат 🚫
3. Без политики и религии 🚫
4. Шутки — без обид 🤗
5. 18+ запрещено 🚫
"""

BAD_WORDS = [
    "сук", "бля", "пизд", "пидор", "еб", "уеб",
    "долбоеб", "мудак", "гондон", "шлюх",
    "чмо", "твар", "лох", "даун", "хуй"
]

REPLACE_MAP = {
    "0": "о", "1": "и", "3": "е", "4": "а", "5": "с",
    "@": "а", "$": "с", "!": "и",
    "p": "п", "x": "х", "y": "у", "e": "е",
    "a": "а", "o": "о", "c": "с", "k": "к"
}

last_messages = {}
violations = {}

# ---------- функции ----------

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(RULES_TEXT)

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Добро пожаловать, {user.first_name}!\n"
            "📌 Напиши /rules чтобы прочитать правила."
        )

def is_flood(user_id):
    now = time.time()
    times = last_messages.get(user_id, [])
    times = [t for t in times if now - t < 5]
    times.append(now)
    last_messages[user_id] = times
    return len(times) > 5

def normalize(text):
    text = text.lower()
    for k, v in REPLACE_MAP.items():
        text = text.replace(k, v)
    return re.sub(r"[^а-яё]", "", text)

def check_antimat(user_id, text):
    clean = normalize(text)
    if any(w in clean for w in BAD_WORDS):
        violations[user_id] = violations.get(user_id, 0) + 1
        if violations[user_id] >= 2:
            violations[user_id] = 0
            return True
    return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    text = update.message.text

    if is_flood(user_id):
        await update.message.reply_text("⚠️ Не флудите!")
        return

    if check_antimat(user_id, text):
        await update.message.reply_text("🚫 Мат запрещён. Предупреждение сброшено.")
        return

# ---------- запуск ----------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("rules", rules))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущен...")
app.run_polling()
