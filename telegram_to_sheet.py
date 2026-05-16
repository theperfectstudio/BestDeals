import time
import asyncio
import re
import os
import json
import gspread

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from oauth2client.service_account import ServiceAccountCredentials

# =========================================================
# 1. GitHub Secrets માંથી ડેટા મેળવવો
# =========================================================

API_ID = int(os.getenv("API_ID", "35795778"))
API_HASH = os.getenv("API_HASH", "d4256dd43d5184feed3f3680e5f3812f")
SESSION_STR = os.getenv("SESSION_STR")
CREDENTIALS_JSON = os.getenv("CREDENTIALS_JSON")

CHANNEL_USERNAME = "@best_dealsareon"
SHEET_NAME = "EarnKaro_Deals"

# =========================================================
# 2. Google Sheet કનેક્શન
# =========================================================

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
        print(f"❌ Sheet Connection Error: {e}")
        return None

# =========================================================
# 3. Price & Discount Extractor
# =========================================================

def extract_prices_and_discount(text):
    prices = re.findall(
        r'(?:₹|Rs\.?|INR)\s?(\d+(?:,\d+)*)',
        text,
        flags=re.IGNORECASE
    )

    old_price = 0
    new_price = 0
    discount_text = "0%"

    try:
        if len(prices) >= 2:

            p1 = int(prices[0].replace(",", ""))
            p2 = int(prices[1].replace(",", ""))

            old_price = max(p1, p2)
            new_price = min(p1, p2)

            if old_price > 0:
                discount_val = (
                    (old_price - new_price) / old_price
                ) * 100

                discount_text = f"{round(discount_val)}%"

        elif len(prices) == 1:

            new_price = int(prices[0].replace(",", ""))
            old_price = new_price

    except Exception as e:
        print(f"❌ Price Extraction Error: {e}")

    return old_price, new_price, discount_text

# =========================================================
# 4. Telegram Client Setup
# =========================================================

if not SESSION_STR:
    raise Exception("❌ SESSION_STR Secret Missing")

client = TelegramClient(
    StringSession(SESSION_STR),
    API_ID,
    API_HASH
)

# =========================================================
# 5. Sheet Instance (એકવાર જ connect કરવું)
# =========================================================

sheet = connect_sheet()

# =========================================================
# 6. Telegram Message Handler
# =========================================================

@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handler(event):

    try:
        msg_text = event.message.message

        if not msg_text:
            return

        print("\n📩 નવી પોસ્ટ મળી...")

        # બધા URLs શોધો
        urls = re.findall(r'(https?://\S+)', msg_text)

        if not urls:
            print("⚠️ URL મળ્યો નહીં")
            return

        profit_link = urls[0]

        image_url = (
            urls[1]
            if len(urls) > 1
            else "No Image URL"
        )

        # Title
        title = msg_text.split("\n")[0][:150]

        # Price Extract
        old_p, new_p, discount = extract_prices_and_discount(msg_text)

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        row_data = [
            timestamp,
            title,
            image_url,
            old_p,
            new_p,
            discount,
            profit_link
        ]

        # Google Sheet માં Save
        if sheet:
            sheet.append_row(row_data)

            print("✅ Deal Saved Successfully")
            print(f"📝 {title}")

        else:
            print("❌ Sheet not connected")

    except Exception as e:
        print(f"❌ Handler Error: {e}")

# =========================================================
# 7. Main Function
# =========================================================

async def main():

    print(
        f"🚀 GitHub Action Bot Started & Listening to {CHANNEL_USERNAME}..."
    )

    # Telegram Connect
    await client.start()

    print("✅ Telegram Client Connected")

    # Disconnect સુધી live રાખવું
    await client.run_until_disconnected()

# =========================================================
# 8. Start Bot
# =========================================================

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("🛑 Bot Stopped")

    except Exception as e:
        print(f"❌ Main Error: {e}")
