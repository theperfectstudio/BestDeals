import asyncio
import os
import re
import json
import time
import gspread

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from oauth2client.service_account import ServiceAccountCredentials

# =====================================================
# CONFIG
# =====================================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STR = os.getenv("SESSION_STR")
CREDENTIALS_JSON = os.getenv("CREDENTIALS_JSON")

CHANNEL_USERNAME = "@best_dealsareon"
SHEET_NAME = "EarnKaro_Deals"

JSON_FILE = "deals.json"
IMAGE_FOLDER = "images"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

# =====================================================
# GOOGLE SHEET CONNECTION
# =====================================================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(CREDENTIALS_JSON)

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict,
    scope
)

gspread_client = gspread.authorize(creds)

sheet = gspread_client.open(SHEET_NAME).sheet1

print("✅ Google Sheet Connected")

# =====================================================
# LOAD EXISTING JSON
# =====================================================

if os.path.exists(JSON_FILE):

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        deals = json.load(f)

else:

    deals = []
    asyncio.run(main())
