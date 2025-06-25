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

# تعريف حالات المحادثة
NAME, PROJECT, UNIV, COLLEGE, DEPARTMENT, STAGE, SUBJECT, DOCTOR, DESC = range(9)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("📌 اسم الطالب:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📌 اسم المشروع:")
    return PROJECT

async def get_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['project'] = update.message.text
    await update.message.reply_text("🏛️ اسم الجامعة (اختياري):")
    return UNIV

async def get_univ(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['univ'] = update.message.text
    await update.message.reply_text("🏫 اسم الكلية:")
    return COLLEGE

async def get_college(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['college'] = update.message.text
    await update.message.reply_text("📚 القسم:")
    return DEPARTMENT

async def get_department(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['department'] = update.message.text
    await update.message.reply_text("📖 المرحلة:")
    return STAGE

async def get_stage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['stage'] = update.message.text
    await update.message.reply_text("🧪 اسم المادة:")
    return SUBJECT

async def get_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['subject'] = update.message.text
    await update.message.reply_text("👨‍🏫 اسم الدكتور (اختياري):")
    return DOCTOR

async def get_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['doctor'] = update.message.text
    await update.message.reply_text("📝 اكتب وصف التقرير وعدد الصفحات المطلوبة (مثلاً: 3 صفحات)")
    return DESC

async def get_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['desc'] = update.message.text
    await generate_pdf(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ تم إلغاء العملية")
    return ConversationHandler.END

async def generate_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        filename = f"report_{user_id}.pdf"
        
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # صفحة الغلاف
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height-100, f"تقرير: {context.user_data['project']}")
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height-140, f"الطالب: {context.user_data['name']}")
        
        # معلومات إضافية
        y_pos = height-160
        for key in ['univ', 'college', 'department', 'stage', 'subject', 'doctor']:
            if key in context.user_data and context.user_data[key]:
                c.drawCentredString(width/2, y_pos, f"{key.capitalize()}: {context.user_data[key]}")
                y_pos -= 20
        
        c.showPage()
        
        # محتوى التقرير
        try:
            pages = max(1, int(''.join(filter(str.isdigit, context.user_data['desc']))))
        except:
            pages = 1
            
        for page in range(pages):
            c.setFont("Helvetica", 14)
            c.drawString(50, height-50, f"الصفحة {page+1}")
            c.setFont("Helvetica", 12)
            text = c.beginText(50, height-100)
            text.textLines(context.user_data['desc'])
            c.drawText(text)
            if page < pages-1:
                c.showPage()
        
        c.save()
        
        with open(filename, "rb") as file:
            await update.message.reply_document(
                document=file,
                caption="✅ تم إنشاء التقرير بنجاح"
            )
        
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_project)],
            UNIV: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_univ)],
            COLLEGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_college)],
            DEPARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_department)],
            STAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_stage)],
            SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_subject)],
            DOCTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_doctor)],
            DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_desc)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv_handler)
    print("🚀 البوت يعمل والانتظار للرسائل...")
    app.run_polling()
