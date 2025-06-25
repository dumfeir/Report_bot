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
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

# تعريف حالات المحادثة
(STUDENT, PROJECT, UNIVERSITY, COLLEGE, 
 DEPARTMENT, LEVEL, COURSE, PROFESSOR, 
 DESCRIPTION) = range(9)

# تهيئة OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

async def generate_ai_report(topic: str, pages: int) -> str:
    """إنشاء محتوى التقرير باستخدام الذكاء الاصطناعي"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional academic writer. Write detailed reports in Arabic."},
                {"role": "user", "content": f"اكتب تقريرًا أكاديميًا مفصلًا حول {topic} بمقدار {pages} صفحات. استخدم عناوين واضحة وتنسيق أكاديمي."}
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

# ... [جميع دوال جمع البيانات كما هي في الكود السابق]

async def report_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['description'] = update.message.text
    await update.message.reply_text("⏳ جاري إنشاء التقرير باستخدام الذكاء الاصطناعي...")
    await generate_report(update, context)
    return ConversationHandler.END

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # استخراج عدد الصفحات من الوصف
        try:
            pages = max(1, int(''.join(filter(str.isdigit, context.user_data['description'])))
        except:
            pages = 3  # القيمة الافتراضية
            
        # إنشاء المحتوى باستخدام الذكاء الاصطناعي
        ai_content = await generate_ai_report(
            context.user_data['description'], 
            pages
        )
        
        if not ai_content:
            raise Exception("فشل في إنشاء المحتوى باستخدام الذكاء الاصطناعي")
        
        # إنشاء ملف PDF
        filename = "academic_report.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # صفحة الغلاف
        story.append(Paragraph("التقرير الأكاديمي", styles['Title']))
        story.append(Spacer(1, 24))
        story.append(Paragraph(f"إعداد: {context.user_data['student']}", styles['Normal']))
        story.append(PageBreak())
        
        # محتوى التقرير
        story.append(Paragraph(ai_content, styles['Normal']))
        doc.build(story)
        
        # إرسال الملف
        with open(filename, "rb") as file:
            await update.message.reply_document(
                document=file,
                caption="✅ تم إنشاء التقرير بنجاح"
            )
        
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

# ... [بقية الكود كما هي]
