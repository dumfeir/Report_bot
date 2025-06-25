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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# تعريف حالات المحادثة
(STUDENT, PROJECT, UNIVERSITY, COLLEGE, 
 DEPARTMENT, LEVEL, COURSE, PROFESSOR, 
 DESCRIPTION) = range(9)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "📌 Please enter student full name:"
    )
    return STUDENT

async def student_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['student'] = update.message.text
    await update.message.reply_text(
        "📌 Enter project title:"
    )
    return PROJECT

async def project_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['project'] = update.message.text
    await update.message.reply_text(
        "🏛️ Enter university name (optional):"
    )
    return UNIVERSITY

async def university_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['university'] = update.message.text
    await update.message.reply_text(
        "🏫 Enter college/faculty name:"
    )
    return COLLEGE

async def college_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['college'] = update.message.text
    await update.message.reply_text(
        "📚 Enter department name:"
    )
    return DEPARTMENT

async def department_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['department'] = update.message.text
    await update.message.reply_text(
        "📖 Enter academic level (e.g., Bachelor 4):"
    )
    return LEVEL

async def academic_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['level'] = update.message.text
    await update.message.reply_text(
        "🧪 Enter course name:"
    )
    return COURSE

async def course_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['course'] = update.message.text
    await update.message.reply_text(
        "👨‍🏫 Enter professor name (optional):"
    )
    return PROFESSOR

async def professor_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['professor'] = update.message.text
    await update.message.reply_text(
        "📝 Enter report description and number of pages needed (e.g., 5 pages):"
    )
    return DESCRIPTION

async def report_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['description'] = update.message.text
    await generate_report(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ Operation cancelled"
    )
    return ConversationHandler.END

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        filename = "academic_report.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Cover Page
        story.append(Paragraph("ACADEMIC REPORT", styles['Title']))
        story.append(Spacer(1, 24))
        
        story.append(Paragraph(f"<b>Project Title:</b> {context.user_data['project']}", styles['Normal']))
        story.append(Paragraph(f"<b>Prepared by:</b> {context.user_data['student']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Academic Information
        info_items = [
            ('University', context.user_data.get('university', 'N/A')),
            ('College', context.user_data['college']),
            ('Department', context.user_data['department']),
            ('Level', context.user_data['level']),
            ('Course', context.user_data['course']),
            ('Professor', context.user_data.get('professor', 'N/A'))
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
                story.append(Paragraph(f"Page {page+1}", styles['Heading3']))
                story.append(Spacer(1, 12))
            
            story.append(Paragraph(context.user_data['description'], styles['Normal']))
            if page < pages - 1:
                story.append(PageBreak())
        
        doc.build(story)
        
        with open(filename, "rb") as file:
            await update.message.reply_document(
                document=file,
                caption="✅ Your academic report has been generated successfully"
            )
        
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error generating report: {str(e)}"
        )

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    
    if not TOKEN:
        print("❌ Error: BOT_TOKEN environment variable is missing!")
        exit(1)
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STUDENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_name)],
            PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, project_title)],
            UNIVERSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, university_name)],
            COLLEGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, college_name)],
            DEPARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, department_name)],
            LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, academic_level)],
            COURSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, course_name)],
            PROFESSOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, professor_name)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_description)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", lambda u,c: u.message.reply_text("Use /start to begin creating your academic report")))
    
    print("🚀 Academic Report Bot is running...")
    app.run_polling()
