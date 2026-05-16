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

# =====================================================
# TELEGRAM CLIENT
# =====================================================

client = TelegramClient(
    StringSession(SESSION_STR),
    API_ID,
    API_HASH
)

# =====================================================
# PRICE EXTRACTOR
# =====================================================


def extract_prices(text):

    prices = re.findall(
        r'(?:₹|Rs\.?|INR)\s?(\d+(?:,\d+)*)',
        text,
        flags=re.IGNORECASE
    )

    old_price = 0
    new_price = 0
    discount = "0%"

    try:

        if len(prices) >= 2:

            p1 = int(prices[0].replace(',', ''))
            p2 = int(prices[1].replace(',', ''))

            old_price = max(p1, p2)
            new_price = min(p1, p2)

            if old_price > 0:

                disc = (
                    (old_price - new_price)
                    / old_price
                ) * 100

                discount = f"{round(disc)}% OFF"

        elif len(prices) == 1:

            new_price = int(prices[0].replace(',', ''))
            old_price = new_price

    except:
        pass

    return old_price, new_price, discount

# =====================================================
# MESSAGE HANDLER
# =====================================================

@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handler(event):

    try:

        text = event.message.message or ""

        if not text:
            return

        print("\n📩 New Telegram Deal Received")

        # =================================================
        # EXTRACT LINKS
        # =================================================

        urls = re.findall(
            r'(https?://\S+)',
            text
        )

        main_link = urls[0] if urls else "#"

        # =================================================
        # TITLE
        # =================================================

        title = text.split("\n")[0][:180]

        # =================================================
        # PRICES
        # =================================================

        old_price, new_price, discount = (
            extract_prices(text)
        )

        # =================================================
        # DOWNLOAD IMAGE
        # =================================================

        image_path = ""

        if event.photo:

            image_path = await event.download_media(
                file=f"{IMAGE_FOLDER}/"
            )

            print("🖼 Banner Downloaded")

        # =================================================
        # TIMESTAMP
        # =================================================

        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # =================================================
        # STORE DETECTION
        # =================================================

        store = "Store"

        lower = text.lower()

        if "amazon" in lower:
            store = "Amazon"

        elif "flipkart" in lower:
            store = "Flipkart"

        elif "myntra" in lower:
            store = "Myntra"

        elif "ajio" in lower:
            store = "Ajio"

        elif "nykaa" in lower:
            store = "Nykaa"

        # =================================================
        # DEAL OBJECT
        # =================================================

        deal = {
            "id": timestamp,
            "title": title,
            "caption": text,
            "image": image_path,
            "old_price": old_price,
            "new_price": new_price,
            "discount": discount,
            "main_link": main_link,
            "all_links": urls,
            "store": store,
            "date": timestamp
        }

        # =================================================
        # INSERT LATEST FIRST
        # =================================================

        deals.insert(0, deal)

        # =================================================
        # SAVE JSON
        # =================================================

        with open(JSON_FILE, "w", encoding="utf-8") as f:

            json.dump(
                deals,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("✅ JSON Updated")

        # =================================================
        # SAVE GOOGLE SHEET
        # =================================================

        sheet.append_row([
            timestamp,
            title,
            image_path,
            old_price,
            new_price,
            discount,
            main_link,
            store,
            text
        ])

        print("✅ Google Sheet Updated")

    except Exception as e:

        print(f"❌ Error: {e}")

# =====================================================
# MAIN
# =====================================================

async def main():

    print(f"🚀 Listening To {CHANNEL_USERNAME}")

    await client.start()

    print("✅ Telegram Connected")

    await client.run_until_disconnected()

if __name__ == "__main__":

    asyncio.run(main())
