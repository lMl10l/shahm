from telethon.sync import TelegramClient, events
import logging

api_id = '12706503'
api_hash = '4344a75f9ae9d1d03f577b61e7313884'
bot_token = '5970239537:AAF8OqpJ8kZMNXyZcfnCuJwQ0ZalW_KZ4DA'
owner_id = '5564802580'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    if event.from_id == owner_id:
        return
    await client.forward_messages(owner_id, event.message)

if __name__ == '__main__':
    with client:
        client.run_until_disconnected()