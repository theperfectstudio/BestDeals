import asyncio
import re
import os
import json
import time
import gspread

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from oauth2client.service_account import ServiceAccountCredentials

# =====================================================
# ENV VARIABLES
# =====================================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STR = os.getenv("SESSION_STR")
CREDENTIALS_JSON = os.getenv("CREDENTIALS_JSON")

CHANNEL_USERNAME = "@best_dealsareon"

SHEET_NAME = "EarnKaro_Deals"

JSON_FILE = "deals.json"

IMAGE_FOLDER = "images"

# =====================================================
# CREATE IMAGE FOLDER
# =====================================================

os.makedirs(IMAGE_FOLDER, exist_ok=True)

# =====================================================
# GOOGLE SHEET CONNECTION
# =====================================================

def connect_sheet():

    try:

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

        print("✅ Google Sheet Connected")

        return gspread_client.open(SHEET_NAME).sheet1

    except Exception as e:

        print(f"❌ Sheet Error: {e}")

        return None

# =====================================================
# LOAD EXISTING JSON
# =====================================================

def load_existing_deals():

    if os.path.exists(JSON_FILE):

        try:

            with open(JSON_FILE, "r", encoding="utf-8") as f:

                return json.load(f)

        except Exception:

            return []

    return []

# =====================================================
# SAVE JSON
# =====================================================

def save_deals_json(data):

    with open(JSON_FILE, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

# =====================================================
# EXTRACT PRICES
# =====================================================

def extract_prices_and_discount(text):

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

            p1 = int(prices[0].replace(",", ""))
            p2 = int(prices[1].replace(",", ""))

            old_price = max(p1, p2)

            new_price = min(p1, p2)

            if old_price > 0:

                discount_val = (
                    (old_price - new_price)
                    / old_price
                ) * 100

                discount = f"{round(discount_val)}%"

        elif len(prices) == 1:

            new_price = int(prices[0].replace(",", ""))

            old_price = new_price

    except Exception as e:

        print(f"❌ Price Error: {e}")

    return old_price, new_price, discount

# =====================================================
# CONNECT SHEET
# =====================================================

sheet = connect_sheet()

# =====================================================
# LOAD DEALS
# =====================================================

deals_data = load_existing_deals()

# =====================================================
# TELEGRAM CLIENT
# =====================================================

client = TelegramClient(
    StringSession(SESSION_STR),
    API_ID,
    API_HASH
)

# =====================================================
# MESSAGE HANDLER
# =====================================================

@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handler(event):

    try:

        msg_text = event.message.message or ""

        if not msg_text:
            return

        print("\n📩 New Deal Received")

        # =================================================
        # EXTRACT URLS
        # =================================================

        urls = re.findall(
            r'(https?://\S+)',
            msg_text
        )

        if not urls:

            print("⚠️ No URL Found")

            return

        main_link = urls[0]

        # =================================================
        # TITLE
        # =================================================

        title = msg_text.split("\n")[0][:150]

        # =================================================
        # PRICES
        # =================================================

        old_price, new_price, discount = (
            extract_prices_and_discount(msg_text)
        )

        # =================================================
        # TIMESTAMP
        # =================================================

        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # =================================================
        # DOWNLOAD TELEGRAM IMAGE
        # =================================================

        image_path = ""

        if event.photo:

            try:

                image_path = await event.download_media(
                    file=f"{IMAGE_FOLDER}/"
                )

                print("🖼 Image Downloaded")

            except Exception as e:

                print(f"❌ Image Error: {e}")

        # =================================================
        # CREATE DEAL OBJECT
        # =================================================

        deal = {

            "id": timestamp,

            "title": title,

            "full_text": msg_text,

            "image": image_path,

            "old_price": old_price,

            "new_price": new_price,

            "discount": discount,

            "main_link": main_link,

            "all_links": urls,

            "date": timestamp
        }

        # =================================================
        # SAVE TO JSON
        # =================================================

        deals_data.insert(0, deal)

        save_deals_json(deals_data)

        print("✅ JSON Updated")

        # =================================================
        # SAVE TO GOOGLE SHEET
        # =================================================

        if sheet:

            row = [

                timestamp,

                title,

                image_path,

                old_price,

                new_price,

                discount,

                main_link,

                ", ".join(urls)

            ]

            sheet.append_row(row)

            print("✅ Google Sheet Updated")

    except Exception as e:

        print(f"❌ Handler Error: {e}")

# =====================================================
# MAIN
# =====================================================

async def main():

    print(f"🚀 Listening to {CHANNEL_USERNAME}")

    await client.start()

    print("✅ Telegram Connected")

    await client.run_until_disconnected()

# =====================================================
# START
# =====================================================

if __name__ == "__main__":

    asyncio.run(main())
