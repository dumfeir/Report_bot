import os
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from fpdf import FPDF

# تعريف حالات المحادثة
(STUDENT, PROJECT, TOPIC, PAGES) = range(4)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Academic Report', 0, 1, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

async def generate_ai_report(topic: str, pages: int) -> str:
    """إنشاء محتوى التقرير باستخدام الذكاء الاصطناعي"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional academic writer."},
                {"role": "user", "content": f"Write a detailed {pages}-page academic report about {topic} in Arabic with sections and subsections."}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI Error: {str(e)}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("📌 اسم الطالب الكامل:")
    return STUDENT

async def get_student(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['student'] = update.message.text
    await update.message.reply_text("📌 عنوان المشروع:")
    return PROJECT

async def get_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['project'] = update.message.text
    await update.message.reply_text("🧠 موضوع التقرير (مثال: البوابات المنطقية):")
    return TOPIC

async def get_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['topic'] = update.message.text
    await update.message.reply_text("📝 عدد الصفحات المطلوبة (مثال: 3):")
    return PAGES

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        pages = int(context.user_data.get('pages', 3))
        await update.message.reply_text("⏳ جاري إنشاء التقرير باستخدام الذكاء الاصطناعي...")
        
        ai_content = await generate_ai_report(context.user_data['topic'], pages)
        if not ai_content:
            raise Exception("فشل في إنشاء المحتوى")
        
        # إنشاء PDF
        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # صفحة الغلاف
        pdf.chapter_title(f"تقرير عن: {context.user_data['topic']}")
        pdf.chapter_body(f"إعداد: {context.user_data['student']}\nالمشروع: {context.user_data['project']}")
        
        # محتوى التقرير
        pdf.add_page()
        pdf.chapter_body(ai_content)
        
        # حفظ وإرسال الملف
        filename = "academic_report.pdf"
        pdf.output(filename)
        
        with open(filename, "rb") as file:
            await update.message.reply_document(
                document=file,
                caption=f"✅ تقرير جاهز: {context.user_data['topic']}"
            )
        
        os.remove(filename)
        return ConversationHandler.END
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ تم الإلغاء")
    return ConversationHandler.END

if __name__ == "__main__":
    # تهيئة OpenAI
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    # تهيئة البوت
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("❌ خطأ: لم يتم تعيين BOT_TOKEN")
        exit(1)
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STUDENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_student)],
            PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_project)],
            TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_topic)],
            PAGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_report)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv_handler)
    print("🚀 البوت يعمل...")
    app.run_polling()
