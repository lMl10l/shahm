from telethon import events
import logging
from config import *

owner_id = 705475246

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

@client.on(events.NewMessage)
async def forward_message(event):
    if event.text:
        try:
            if event.is_private and event.sender_id != owner_id:
                await event.forward_to(owner_id)
        except ValueError:
            pass

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('مرحباً بك في بوت تواصل لسورس الجوكر ')

with client:
    client.run_until_disconnected()