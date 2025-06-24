import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from random import randint

TOKEN = "7588023257:AAGFtTg8bVsTpGWRP4zeCNsqlLvkySfmEA0"
ADMIN_IDS = [123456789]  # Твой Telegram ID сюда, чтобы делать админ-команды

BALANCE_FILE = "balances.json"

def load_balances():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_balances(balances):
    with open(BALANCE_FILE, "w") as f:
        json.dump(balances, f)

user_balances = load_balances()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Открыть кейс 🎁", web_app=WebAppInfo("https://slightmoon-coder.github.io/telegram-mini-app/"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Открывай кейс через кнопку ниже или отправь сообщение с текстом 'подарок', чтобы получить подарки и открыть кейс вручную.\n"
        "Чтобы узнать баланс — введи /balance\nДля помощи — /help", reply_markup=reply_markup)

async def gift_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.lower()
    if "подарок" in text:
        user_balances[user_id] = user_balances.get(user_id, 0) + 1
        save_balances(user_balances)
        await update.message.reply_text("Подарок получен! 🎉 Готов открыть кейс? Напиши /open или нажми кнопку ниже.")
    else:
        await update.message.reply_text("Чтобы получить подарок, отправь слово 'подарок'.")

async def open_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    balance = user_balances.get(user_id, 0)

    if balance < 1:
        await update.message.reply_text("Сначала отправь подарок, чтобы открыть кейс.")
        return

    user_balances[user_id] = balance - 1
    save_balances(user_balances)

    outcome = randint(1, 100)
    if outcome <= 5:
        prize = "🔥 Огненный подарок ($1.5)"
    elif outcome <= 30:
        prize = "💰 Подарок на $1.0"
    elif outcome <= 60:
        prize = "📦 Стикерпак ($0.3)"
    else:
        prize = "❌ Ничего не выпало 😢"

    await update.message.reply_text(f"🎉 Ты открыл кейс и получил: {prize}\n(Подарок будет выслан вручную)")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    balance = user_balances.get(user_id, 0)
    await update.message.reply_text(f"У тебя {balance} подарков.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — Запуск бота и кнопка кейса\n"
        "/balance — Показать баланс подарков\n"
        "/open — Открыть кейс (тратит подарок)\n"
        "/addgift <user_id> <кол-во> — (админ) добавить подарки пользователю")

async def addgift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У тебя нет прав на выполнение этой команды.")
        return

    try:
        args = context.args
        if len(args) != 2:
            raise ValueError
        target_id = args[0]
        amount = int(args[1])
    except:
        await update.message.reply_text("Использование: /addgift <user_id> <кол-во>")
        return

    user_balances[target_id] = user_balances.get(target_id, 0) + amount
    save_balances(user_balances)
    await update.message.reply_text(f"Добавлено {amount} подарков пользователю {target_id}.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("open", open_case))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("addgift", addgift))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gift_received))

app.run_polling()
