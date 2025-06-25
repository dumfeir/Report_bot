import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

QUESTIONS = [
    "📌 اسم الطالب:",
    "📌 اسم المشروع:",
    "🏛️ اسم الجامعة (اختياري):",
    "🏫 اسم الكلية:",
    "📚 القسم:",
    "📖 المرحلة:",
    "🧪 اسم المادة:",
    "👨‍🏫 اسم الدكتور (اختياري):",
    "📝 اكتب وصف التقرير وعدد الصفحات المطلوبة (مثلاً: 3 صفحات)"
]

user_answers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_answers[user_id] = []
    await update.message.reply_text("أهلاً بك! سأطرح عليك بعض الأسئلة لإنشاء تقرير PDF.\n\nأجب على كل سؤال بدقة.")
    await update.message.reply_text(QUESTIONS[0])
    return 0

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_answers:
        await update.message.reply_text("الرجاء البدء بالضغط على /start")
        return ConversationHandler.END
    
    user_answers[user_id].append(update.message.text)
    next_state = len(user_answers[user_id])
    
    if next_state < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[next_state])
        return next_state
    else:
        await update.message.reply_text("⏳ جاري إنشاء التقرير...")
        await generate_pdf_and_send(update, context, user_answers[user_id])
        del user_answers[user_id]
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_answers:
        del user_answers[user_id]
    await update.message.reply_text("❌ تم إلغاء العملية.")
    return ConversationHandler.END

async def generate_pdf_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, answers):
    user_id = update.message.from_user.id
    filename = f"report_{user_id}.pdf"
    
    try:
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # الغلاف
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height-100, f"تقرير: {answers[1]}")
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height-140, f"الطالب: {answers[0]}")
        
        # باقي المعلومات
        y_position = height - 160
        for answer, question in zip(answers[2:8], QUESTIONS[2:8]):
            if answer and "اختياري" not in question:
                c.drawCentredString(width/2, y_position, f"{question.split(':')[0]}: {answer}")
                y_position -= 20
        
        c.showPage()
        
        # محتوى التقرير
        try:
            pages = max(1, int(''.join(filter(str.isdigit, answers[8]))))
        except:
            pages = 1
            
        for page_num in range(pages):
            c.setFont("Helvetica", 14)
            c.drawString(50, height-50, f"الصفحة {page_num+1}")
            c.setFont("Helvetica", 12)
            text = c.beginText(50, height-100)
            text.textLines(answers[8])
            c.drawText(text)
            if page_num < pages - 1:
                c.showPage()
        
        c.save()
        
        with open(filename, "rb") as file:
            await update.message.reply_document(document=file)
            
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {str(e)}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    TOKEN = "ضع_توكن_البوت_هنا"  # أو استخدم os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            i: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]
            for i in range(len(QUESTIONS))
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv_handler)
    print("Bot is running...")
    app.run_polling()
