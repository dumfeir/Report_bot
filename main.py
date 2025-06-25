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
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

# قاموس الترجمة (يمكن تطويره)
TRANSLATIONS = {
    'جامعة': 'University',
    'كلية': 'College',
    'هندسة': 'Engineering',
    'علوم': 'Science',
    'طب': 'Medicine',
    'بكالوريوس': 'Bachelor',
    'ماجستير': 'Master',
    'دكتوراه': 'PhD',
    # أضف المزيد حسب الحاجة
}

def translate_to_english(text):
    """ترجمة بسيطة للنصوص العربية إلى الإنجليزية"""
    if not isinstance(text, str):
        return text
        
    for ar, en in TRANSLATIONS.items():
        text = text.replace(ar, en)
    return text

# تعريف حالات المحادثة
(STUDENT, PROJECT, UNIVERSITY, COLLEGE, 
 DEPARTMENT, LEVEL, COURSE, PROFESSOR, 
 DESCRIPTION) = range(9)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("📌 اسم الطالب الكامل:")
    return STUDENT

async def student_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['student'] = update.message.text
    await update.message.reply_text("📌 عنوان المشروع:")
    return PROJECT

async def project_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['project'] = update.message.text
    await update.message.reply_text("🏛️ اسم الجامعة (اختياري):")
    return UNIVERSITY

async def university_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['university'] = update.message.text
    await update.message.reply_text("🏫 اسم الكلية:")
    return COLLEGE

async def college_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['college'] = update.message.text
    await update.message.reply_text("📚 القسم:")
    return DEPARTMENT

async def department_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['department'] = update.message.text
    await update.message.reply_text("📖 المستوى الأكاديمي (مثال: بكالوريوس 4):")
    return LEVEL

async def academic_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['level'] = update.message.text
    await update.message.reply_text("🧪 اسم المادة:")
    return COURSE

async def course_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['course'] = update.message.text
    await update.message.reply_text("👨‍🏫 اسم الأستاذ (اختياري):")
    return PROFESSOR

async def professor_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['professor'] = update.message.text
    await update.message.reply_text("📝 وصف التقرير وعدد الصفحات المطلوبة (مثال: 5 صفحات):")
    return DESCRIPTION

async def report_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['description'] = update.message.text
    await generate_report(update, context)
    return ConversationHandler.END

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        filename = "academic_report.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        
        styles = getSampleStyleSheet()
        story = []
        
        # ترجمة البيانات إلى الإنجليزية
        translated_data = {
            'student': translate_to_english(context.user_data['student']),
            'project': translate_to_english(context.user_data['project']),
            'university': translate_to_english(context.user_data.get('university', 'N/A')),
            'college': translate_to_english(context.user_data['college']),
            'department': translate_to_english(context.user_data['department']),
            'level': translate_to_english(context.user_data['level']),
            'course': translate_to_english(context.user_data['course']),
            'professor': translate_to_english(context.user_data.get('professor', 'N/A')),
            'description': translate_to_english(context.user_data['description'])
        }
        
        # Cover Page
        story.append(Paragraph("ACADEMIC REPORT", styles['Title']))
        story.append(Spacer(1, 24))
        
        story.append(Paragraph(f"<b>Project Title:</b> {translated_data['project']}", styles['Normal']))
        story.append(Paragraph(f"<b>Prepared by:</b> {translated_data['student']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Academic Information
        info_items = [
            ('University', translated_data['university']),
            ('College', translated_data['college']),
            ('Department', translated_data['department']),
            ('Level', translated_data['level']),
            ('Course', translated_data['course']),
            ('Professor', translated_data['professor'])
        ]
        
        for item in info_items:
            story.append(Paragraph(f"<b>{item[0]}:</b> {item[1]}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Report Content
        story.append(Spacer(1, 24))
        story.append(Paragraph("REPORT CONTENT", styles['Heading2']))
        
        try:
            pages = max(1, int(''.join(filter(str.isdigit, context.user_data['description']))))
        except:
            pages = 1
            
        for page in range(pages):
            if page > 0:
                story.append(PageBreak())
                story.append(Paragraph(f"Page {page+1}", styles['Heading3']))
                story.append(Spacer(1, 12))
            
            story.append(Paragraph(translated_data['description'], styles['Normal']))
        
        doc.build(story)
        
        with open(filename, "rb") as file:
            await update.message.reply_document(
                document=file,
                caption="✅ تم إنشاء التقرير بنجاح | Report generated successfully"
            )
        
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في إنشاء التقرير | Error generating report: {str(e)}")

# ... [بقية الكود كما هي]
