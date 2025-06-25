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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register English/Arabic supported font
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

# Conversation states
STUDENT_NAME, PROJECT_NAME, UNIVERSITY, COLLEGE, DEPARTMENT, STAGE, SUBJECT, PROFESSOR, REPORT_DESC = range(9)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("📌 Student Name:")
    return STUDENT_NAME

async def get_student_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['student_name'] = update.message.text
    await update.message.reply_text("📌 Project Name:")
    return PROJECT_NAME

async def get_project_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['project_name'] = update.message.text
    await update.message.reply_text("🏛️ University (optional):")
    return UNIVERSITY

# ... [continue with other state handlers]

async def generate_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        filename = "academic_report.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Set English font
        c.setFont("Arial", 12)
        
        # Cover Page
        c.drawString(100, 700, f"Academic Report: {context.user_data['project_name']}")
        c.drawString(100, 680, f"Prepared by: {context.user_data['student_name']}")
        
        # Report Content
        y_position = 650
        c.drawString(100, y_position, f"University: {context.user_data.get('university', 'N/A')}")
        y_position -= 20
        c.drawString(100, y_position, f"College: {context.user_data['college']}")
        y_position -= 20
        # ... [add other fields]
        
        # Report pages
        try:
            pages = max(1, int(''.join(filter(str.isdigit, context.user_data['report_desc'])))
        except:
            pages = 1
            
        for page in range(pages):
            c.showPage()
            c.setFont("Arial", 12)
            c.drawString(100, 700, f"Report Page {page+1} of {pages}")
            c.drawString(100, 680, context.user_data['report_desc'])
        
        c.save()
        
        with open(filename, "rb") as file:
            await update.message.reply_document(
                document=file,
                caption="✅ Report generated successfully"
            )
        
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STUDENT_NAME: [MessageHandler(filters.TEXT, get_student_name)],
            PROJECT_NAME: [MessageHandler(filters.TEXT, get_project_name)],
            # ... [other states]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv_handler)
    print("🚀 Bot is running...")
    app.run_polling()
