from telethon import TelegramClient, events
import random
import schedule
import time

api_id = '5116461'
api_hash = 'e9fe4b672f162a27f78d8af54b004e25'
YOUR_OWNER_ID = '705475246'
bot_token = '6330369637:AAGAnd4SsT-WmXgFYU8Zy5q0Dnzw4p7Ow8s'

client = TelegramClient('session_name', api_id, api_hash)

adhkar_list = []
enabled_groups = set()
set_interval = 15
async def send_adhkar():
    if adhkar_list:
        random_adhkar = random.choice(adhkar_list)
        for chat_id in enabled_groups:
            await client.send_message(chat_id, f"*{random_adhkar}*", parse_mode="Markdown")

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.from_id
    if user_id == YOUR_OWNER_ID:
        message = (
            "مرحبًا! اضغط على الروابط أدناه لإضافة الأذكار أو تعيين فاصل زمني:\n\n"
            "[إضافة أذكار](https://t.me/your_bot_username?start=add_adhkar)\n"
            "[تعيين فاصل زمني](https://t.me/your_bot_username?start=set_interval)"
        )
        await event.respond(message, link_preview=False)
    else:
        await event.respond('مرحبًا! لا يمكنك استخدام هذه الأوامر.')
@client.on(events.CallbackQuery)
async def button_click(event):
    if event.data == b'add_adhkar':
        await event.respond("أرسل لي الأذكار التي تريد إضافتها.")
    elif event.data == b'set_interval':
        user_id = event.from_id
        if user_id == YOUR_OWNER_ID:
            await event.respond("أدخل عدد الدقائق لإرسال الأذكار:")
        else:
            await event.respond("ليس لديك الصلاحية لتعيين الفاصل الزمني.")

@client.on(events.NewMessage(pattern='/enable'))
async def enable_group(event):
    chat_id = event.chat_id
    enabled_groups.add(chat_id)
    await event.respond("تم تفعيل الإرسال لهذه المجموعة!")


schedule.every(15).minutes.do(send_adhkar)

client.start()
client.run_until_disconnected()