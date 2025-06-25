from telegram.ext import ApplicationBuilder, CommandHandler

async def start(update, context):
    await update.message.reply_text("✅ البوت يعمل!")

app = ApplicationBuilder().token("BOT_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
