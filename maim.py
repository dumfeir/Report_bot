import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# ترتيب الأسئلة
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

# تحديد حالات المحادثة
QUESTION_STATES = list(range(len(QUESTIONS)))

# تخزين بيانات المستخدمين مؤقتًا
user_answers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_answers[user_id] = []
    await update.message.reply_text("أهلاً بك! سأطرح عليك بعض الأسئلة لإنشاء تقرير PDF.\n\nأجب على كل سؤال بدقة.")
    await update.message.reply_text(QUESTIONS[0])
    return QUESTION_STATES[0]

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_answers:
        await update.message.reply_text("الرجاء البدء بالضغط على /start")
        return ConversationHandler.END
    
    user_answers[user_id].append(update.message.text)

    current_state = len(user_answers[user_id])
    if current_state < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[current_state])
        return QUESTION_STATES[current_state]
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
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # الصفحة الأولى – الغلاف
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 100, f"تقرير بعنوان: {answers[1]}")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 140, f"اسم الطالب: {answers[0]}")
    if answers[2]:
        c.drawCentredString(width / 2, height - 160, f"الجامعة: {answers[2]}")
    c.drawCentredString(width / 2, height - 180, f"الكلية: {answers[3]}")
    c.drawCentredString(width / 2, height - 200, f"القسم: {answers[4]}")
    c.drawCentredString(width / 2, height - 220, f"المرحلة: {answers[5]}")
    c.drawCentredString(width / 2, height - 240, f"المادة: {answers[6]}")
    if answers[7]:
        c.drawCentredString(width / 2, height - 260, f"الدكتور: {answers[7]}")
    c.showPage()

    # باقي الصفحات – وصف التقرير
    try:
        pages = int(''.join(filter(str.isdigit, answers[8]))) or 1
    except:
        pages = 1

    for i in range(pages):
        c.setFont("Helvetica", 14)
        c.drawString(50, height - 100, f"صفحة التقرير {i+1}")
        c.setFont("Helvetica", 12)
        text = c.beginText(50, height - 130)
        text.textLines(answers[8])
        c.drawText(text)
        if i < pages - 1:  # لا تضيف صفحة جديدة بعد الصفحة الأخيرة
            c.showPage()

    c.save()

    await update.message.reply_document(document=open(filename, "rb"))
    os.remove(filename)

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("لم يتم تعيين BOT_TOKEN في متغيرات البيئة")
    
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            state: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]
            for state in QUESTION_STATES
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
