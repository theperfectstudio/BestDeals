import asyncio
import re
import os
import json
import time
import gspread

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from oauth2client.service_account import ServiceAccountCredentials

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STR = os.getenv("SESSION_STR")
CREDENTIALS_JSON = os.getenv("CREDENTIALS_JSON")

CHANNEL_USERNAME = "@best_dealsareon"
SHEET_NAME = "EarnKaro_Deals"

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

        client = gspread.authorize(creds)

        print("✅ Google Sheet Connected")

        return client.open(SHEET_NAME).sheet1

    except Exception as e:

        print(f"❌ Sheet Error: {e}")

        return None

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

            discount_val = (
                (old_price - new_price) / old_price
            ) * 100

            discount = f"{round(discount_val)}%"

        elif len(prices) == 1:

            new_price = int(prices[0].replace(",", ""))
            old_price = new_price

    except Exception as e:

        print(f"❌ Price Error: {e}")

    return old_price, new_price, discount

# =====================================================

sheet = connect_sheet()

client = TelegramClient(
    StringSession(SESSION_STR),
    API_ID,
    API_HASH
)

# =====================================================

@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handler(event):

    try:

        msg_text = event.message.message

        if not msg_text:
            return

        print("📩 New Deal Received")

        urls = re.findall(r'(https?://\S+)', msg_text)

        if not urls:
            return

        profit_link = urls[0]

        image_url = (
            urls[1]
            if len(urls) > 1
            else "No Image"
        )

        title = msg_text.split("\n")[0][:150]

        old_price, new_price, discount = (
            extract_prices_and_discount(msg_text)
        )

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        row = [
            timestamp,
            title,
            image_url,
            old_price,
            new_price,
            discount,
            profit_link
        ]

        if sheet:

            sheet.append_row(row)

            print("✅ Saved:", title)

    except Exception as e:

        print(f"❌ Handler Error: {e}")

# =====================================================

async def main():

    print(f"🚀 Listening to {CHANNEL_USERNAME}")

    await client.start()

    print("✅ Telegram Connected")

    await client.run_until_disconnected()

# =====================================================

if __name__ == "__main__":

    asyncio.run(main())
