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
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# تعريف حالات المحادثة
(STUDENT, PROJECT, UNIVERSITY, COLLEGE, 
 DEPARTMENT, LEVEL, COURSE, PROFESSOR, 
 DESCRIPTION) = range(9)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("📌 اسم الطالب الكامل:")
    return STUDENT

# ... [باقي دوال المحادثة كما هي في الكود السابق]

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        filename = "academic_report.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # صفحة الغلاف
        story.append(Paragraph("التقرير الأكاديمي", styles['Title']))
        story.append(Spacer(1, 24))
        story.append(Paragraph(f"إعداد: {context.user_data['student']}", styles['Normal']))
        
        # محتوى التقرير
        story.append(Spacer(1, 24))
        story.append(Paragraph("وصف التقرير:", styles['Heading2']))
        story.append(Paragraph(context.user_data['description'], styles['Normal']))
        
        doc.build(story)
        
        with open(filename, "rb") as file:
            await update.message.reply_document(
                document=file,
                caption="✅ تم إنشاء التقرير بنجاح"
            )
        
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

# ... [باقي الكود كما هو]
