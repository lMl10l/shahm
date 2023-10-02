import logging
import os
from io import BytesIO
from googletrans import Translator
from PyPDF2 import PdfFileReader
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

SELECTING_ACTION, TRANSLATING = range(2)

translator = Translator()

def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text(
        f"مرحبًا {user.first_name}! يمكنك إرسال ملف PDF بالإنجليزية لترجمته إلى العربية. ابدأ بإرسال الملف."
    )
    return SELECTING_ACTION
def handle_document(update: Update, context: CallbackContext) -> int:
    file = update.message.document
    if file.file_name.endswith('.pdf'):
        file.get_file().download('input.pdf')
        translated_text = translate_pdf('input.pdf')
        
        translated_file = BytesIO()
        translated_file.write(translated_text.encode('utf-8'))
        translated_file.seek(0)
        update.message.reply_document(document=translated_file, filename='translated.pdf')
        return ConversationHandler.END
    else:
        update.message.reply_text("يرجى إرسال ملف بامتداد PDF فقط.")
        return SELECTING_ACTION
def translate_pdf(input_pdf_path):
    with open(input_pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)
        translated_text = ""

        for page_num in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_num)
            page_text = page.extractText()
            translated_page = translator.translate(page_text, src='en', dest='ar')
            translated_text += translated_page.text + '\n'

    return translated_text

def main():
    updater = Updater(token='5970239537:AAF8OqpJ8kZMNXyZcfnCuJwQ0ZalW_KZ4DA', use_context=True)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [MessageHandler(Filters.document.mime_type('application/pdf'), handle_document)],
        },
        fallbacks=[],
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()