from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7588023257:AAGFtTg8bVsTpGWRP4zeCNsqlLvkySfmEA0"

user_balances = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Привет, {user.first_name}! Отправь мне Telegram-подарок и открой кейс 🎁")

async def gift_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Здесь ты вручную фиксируешь что получил подарок
    # (либо сделаем полуавто позже)
    user_balances[user_id] = user_balances.get(user_id, 0) + 1
    await update.message.reply_text("Подарок получен! 🎉 Готов открыть кейс? Напиши /open")

async def open_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from random import randint, choice
    user_id = update.effective_user.id

    if user_balances.get(user_id, 0) < 1:
        await update.message.reply_text("Сначала отправь подарок, чтобы открыть кейс.")
        return

    user_balances[user_id] -= 1

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

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("open", open_case))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gift_received))

app.run_polling()

