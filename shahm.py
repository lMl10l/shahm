import logging
import os
from io import BytesIO
from googletrans import Translator
from PyPDF2 import PdfFileReader
from PIL import Image
import pytesseract
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define states for the conversation
SELECTING_ACTION, TRANSLATING = range(2)

# Initialize the translator
translator = Translator()

# Function to start the conversation
def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text(
        f"مرحبًا {user.first_name}! يمكنك إرسال ملف PDF بالإنجليزية لترجمته إلى العربية. ابدأ بإرسال الملف."
    )
    return SELECTING_ACTION

# Function to handle PDF files
def handle_document(update: Update, context: CallbackContext) -> int:
    file = update.message.document
    if file.mime_type == 'application/pdf':
        # Download the PDF file
        file.get_file().download('input.pdf')
        
        # Check if the PDF contains text or images
        if contains_text('input.pdf'):
            # If it contains text, translate it
            translated_text = translate_pdf_text('input.pdf')
            send_translated_text(update, translated_text)
        else:
            # If it contains images, translate them
            translated_images = translate_pdf_images('input.pdf')
            send_translated_images(update, translated_images)
        
        return ConversationHandler.END
    else:
        update.message.reply_text("يرجى إرسال ملف بامتداد PDF فقط.")
        return SELECTING_ACTION

# Function to check if a PDF contains text
def contains_text(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)
        for page_num in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_num)
            if page.extractText():
                return True
    return False

# Function to translate a PDF with text
def translate_pdf_text(input_pdf_path):
    with open(input_pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)
        translated_text = ""

        for page_num in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_num)
            page_text = page.extractText()
            translated_page = translator.translate(page_text, src='en', dest='ar')
            translated_text += translated_page.text + '\n'

    return translated_text

# Function to translate a PDF with images
def translate_pdf_images(input_pdf_path):
    translated_images = []

    # Convert PDF to images
    images = convert_pdf_to_images(input_pdf_path)

    for image in images:
        # Perform OCR (Optical Character Recognition) on the image
        text = pytesseract.image_to_string(image, lang='eng')
        translated_text = translator.translate(text, src='en', dest='ar').text
        translated_images.append(translated_text)

    return translated_images

# Function to convert PDF to images
def convert_pdf_to_images(pdf_path):
    images = []
    pdf_image_objects = convert_from_path(pdf_path)
    for pdf_image in pdf_image_objects:
        images.append(pdf_image)
    return images

# Function to send the translated text
def send_translated_text(update: Update, translated_text: str):
    update.message.reply_text("هذا هو النص المترجم:")
    update.message.reply_text(translated_text)

# Function to send the translated images
def send_translated_images(update: Update, translated_images: list):
    update.message.reply_text("هذه هي الصور المترجمة:")
    for i, translated_image in enumerate(translated_images, start=1):
        update.message.reply_text(f"صورة {i}:")
        update.message.reply_text(translated_image)

def main():
    updater = Updater(token='5970239537:AAF8OqpJ8kZMNXyZcfnCuJwQ0ZalW_KZ4DA', use_context=True)
    dispatcher = updater.dispatcher

    # Create a conversation handler
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