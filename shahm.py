import schedule
import time
import pickle
import random
from telegram import Bot, Update
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.ext import InlineKeyboardButton, InlineKeyboardMarkup

bot_token = '6330369637:AAGAnd4SsT-WmXgFYU8Zy5q0Dnzw4p7Ow8s'
bot_owner_id = '705475246'

bot = Bot(token=bot_token)
adhkar_list = []
enabled_groups = set()
interval_minutes = 15

def send_adhkar():
    if adhkar_list:
        random_adhkar = random.choice(adhkar_list)
        for chat_id in enabled_groups:
            bot.send_message(chat_id=chat_id, text=random_adhkar, parse_mode=ParseMode.MARKDOWN)

def set_interval(update, context):
    user_id = str(update.message.from_user.id)
    if user_id != bot_owner_id:
        context.bot.send_message(chat_id=update.message.chat_id, text="ليس لديك الصلاحية لتغيير فاصل الزمني.")
        return
    context.bot.send_message(chat_id=update.message.chat_id, text="أدخل عدد الدقائق لإرسال الأذكار:")
    return "WAIT_INTERVAL"

def receive_interval(update, context):
    try:
        global interval_minutes
        interval_minutes = int(update.message.text)
        context.bot.send_message(chat_id=update.message.chat_id, text=f"تم تعيين فاصل زمني للإرسال كل {interval_minutes} دقيقة.")
        schedule.clear()
        schedule.every(interval_minutes).minutes.do(send_adhkar)
        return
    except ValueError:
        context.bot.send_message(chat_id=update.message.chat_id, text="الرجاء إدخال عدد صحيح.")

def start(update, context):
    user_id = str(update.message.from_user.id)
    if user_id == bot_owner_id:
        keyboard = [
            [InlineKeyboardButton("إضافة أذكار", callback_data='add_adhkar')],
            [InlineKeyboardButton("تعيين فاصل زمني", callback_data='set_interval')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('مرحبًا! اضغط على الزر لإضافة الأذكار أو تعيين فاصل زمني:', reply_markup=reply_markup)
    else:
        update.message.reply_text('أنت لا تمتلك الصلاحية لاستخدام هذه الأوامر.')

def button_click(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'add_adhkar':
        context.bot.send_message(chat_id=query.message.chat_id, text="أرسل لي الأذكار التي تريد إضافتها.")
    elif query.data == 'set_interval':
        set_interval(update, context)

def add_adhkar(update, context):
    user_id = str(update.message.from_user.id)
    if user_id == bot_owner_id:
        adhkar_text = update.message.text
        adhkar_list.append(adhkar_text)
        context.bot.send_message(chat_id=update.message.chat_id, text="تمت إضافة الأذكار بنجاح!")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="ليس لديك الصلاحية لإضافة أذكار.")

def enable_group(update, context):
    user_id = str(update.message.from_user.id)
    if user_id == bot_owner_id:
        chat_id = update.message.chat_id
        enabled_groups.add(chat_id)
        context.bot.send_message(chat_id=chat_id, text="تم تفعيل الإرسال لهذه المجموعة!")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="ليس لديك الصلاحية لتفعيل الإرسال للمجموعات.")

schedule.every(interval_minutes).minutes.do(send_adhkar)

updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(button_click))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, add_adhkar))
dispatcher.add_handler(CommandHandler('تفعيل', enable_group))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, receive_interval))

updater.start_polling()

while True:
    schedule.run_pending()
    time.sleep(1)