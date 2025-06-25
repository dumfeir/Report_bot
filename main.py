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
from fpdf.fonts import FontFace

# تعريف حالات المحادثة
(STUDENT, PROJECT, TOPIC, PAGES) = range(4)

class AcademicPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('Noto', '', 'NotoSansArabic-Regular.ttf', uni=True)
        self.set_margins(20, 20, 20)
    
    def header(self):
        self.set_font('Noto', 'B', 16)
        self.cell(0, 10, 'تقرير أكاديمي', 0, 1, 'C')
    
    def chapter_title(self, title):
        self.set_font('Noto', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'R')
        self.ln(5)
    
    def chapter_body(self, body):
        self.set_font('Noto', '', 12)
        self.multi_cell(0, 8, body, align='R')
        self.ln()

async def generate_ai_content(topic: str, pages: int) -> str:
    """إنشاء محتوى التقرير باستخدام الذكاء الاصطناعي"""
    try:
        if not openai.api_key:
            openai.api_key = os.getenv('OPENAI_API_KEY')
            if not openai.api_key:
                raise Exception("OpenAI API key not configured")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an academic expert. Write detailed reports in Arabic with proper formatting."},
                {"role": "user", "content": f"اكتب تقريرًا أكاديميًا عن {topic} بمقدار {pages} صفحات. استخدم عناوين رئيسية وفرعية وتنسيقًا واضحًا."}
            ],
            temperature=0.7,
            max_tokens=2000
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
        pages = max(1, int(update.message.text))
        context.user_data['pages'] = pages
        
        await update.message.reply_text("⏳ جاري إنشاء التقرير باستخدام الذكاء الاصطناعي...")
        
        ai_content = await generate_ai_content(context.user_data['topic'], pages)
        if not ai_content:
            raise Exception("تعذر إنشاء المحتوى. يرجى التأكد من إعدادات OpenAI API")
        
        # إنشاء ملف PDF
        pdf = AcademicPDF()
        pdf.add_page()
        
        # صفحة الغلاف
        pdf.chapter_title(f"عنوان المشروع: {context.user_data['project']}")
        pdf.chapter_body(f"إعداد الطالب: {context.user_data['student']}\nعدد الصفحات: {pages}")
        
        # محتوى التقرير
        pdf.add_page()
        pdf.chapter_title(f"تقرير عن: {context.user_data['topic']}")
        pdf.chapter_body(ai_content)
        
        # حفظ وإرسال الملف
        filename = "academic_report.pdf"
        pdf.output(filename)
        
        with open(filename, "rb") as file:
            await update.message.reply_document(
                document=file,
                caption=f"✅ تم إنشاء التقرير: {context.user_data['project']}"
            )
        
        os.remove(filename)
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ يرجى إدخال رقم صحيح لعدد الصفحات")
        return PAGES
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ تم إلغاء العملية")
    return ConversationHandler.END

if __name__ == "__main__":
    # تهيئة مفاتيح API
    openai.api_key = os.getenv('OPENAI_API_KEY')
    TOKEN = os.getenv('BOT_TOKEN')
    
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
