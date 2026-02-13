import os
from dotenv import load_dotenv

load_dotenv()  # .env faylni yuklaydi

TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
BOT_NAME = os.getenv("BOT_NAME")
