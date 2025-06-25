import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# تعريف الحالات والأسئلة
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

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء المحادثة وإرسال السؤال الأول"""
    user_id = update.message.from_user.id
    user_data[user_id] = {"answers": []}
    await update.message.reply_text("مرحبًا! سأساعدك في إنشاء تقرير أكاديمي.\n\n" + QUESTIONS[0])
    return 0

async def process_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة الإجابات وإرسال الأسئلة التالية"""
    user_id = update.message.from_user.id
    current_state = len(user_data[user_id]["answers"])
    user_data[user_id]["answers"].append(update.message.text)

    if current_state + 1 < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[current_state + 1])
        return current_state + 1
    else:
        await generate_pdf(update, user_data[user_id]["answers"])
        del user_data[user_id]
        return ConversationHandler.END

async def generate_pdf(update: Update, answers: list):
    """إنشاء ملف PDF وإرساله"""
    try:
        user_id = update.message.from_user.id
        filename = f"report_{user_id}.pdf"
        
        # إنشاء PDF
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # صفحة الغلاف
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height-100, "تقرير أكاديمي")
        c.setFont("Helvetica", 14)
        
        y_position = height - 150
        for i, (question, answer) in enumerate(zip(QUESTIONS[:8], answers[:8])):
            if answer and "اختياري" not in question:
                c.drawString(100, y_position, f"{question.split(':')[0]}: {answer}")
                y_position -= 30
        
        c.showPage()
        
        # محتوى التقرير
        try:
            pages = max(1, int(''.join(filter(str.isdigit, answers[8]))))
        except:
            pages = 1
            
        for page in range(pages):
            c.setFont("Helvetica", 12)
            c.drawString(50, height-50, f"الصفحة {page+1} من {pages}")
            text = c.beginText(50, height-100)
            text.textLines(answers[8])
            c.drawText(text)
            if page < pages - 1:
                c.showPage()
        
        c.save()
        
        # إرسال الملف
        with open(filename, 'rb') as file:
            await update.message.reply_document(
                document=file,
                caption="✅ تم إنشاء التقرير بنجاح"
            )
        
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """إلغاء المحادثة"""
    user_id = update.message.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    await update.message.reply_text("تم الإلغاء")
    return ConversationHandler.END

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            i: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_answer)]
            for i in range(len(QUESTIONS))
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", lambda u,c: u.message.reply_text("استخدم /start لبدء إنشاء التقرير")))
    
    print("🚀 البوت يعمل...")
    app.run_polling()
