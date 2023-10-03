from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
api_id = os.environ.get("api_id")
api_hash = os.environ.get("api_hash")
bot_token = os.environ.get("bot_token")
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)