from telethon.sync import TelegramClient, events
import logging

api_id = '12706503'
api_hash = '4344a75f9ae9d1d03f577b61e7313884'
bot_token = '5970239537:AAF8OqpJ8kZMNXyZcfnCuJwQ0ZalW_KZ4DA'
owner_id = '5564802580'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


@client.on(events.NewMessage)
async def forward_message(event):
    if event.text:
        try:
            # إعادة توجيه الرسالة إلى المالك
            forwarded_message = await event.forward_to(int(owner_id))
            response = await client.get_response(forwarded_message)
            await response.reply(event.text)

        except ValueError:
            print("Invalid owner_id. Please make sure it's a valid integer.")
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('مرحبًا بك! أنا بوت تليجرام.')

with client:
    client.run_until_disconnected()