import asyncio
import os
import re
import json
import shutil

from telethon import TelegramClient, events
from telethon.sessions import StringSession

# =====================================================
# CONFIG
# =====================================================

API_ID = int(os.getenv("API_ID"))

API_HASH = os.getenv("API_HASH")

SESSION_STR = os.getenv("SESSION_STR")

CHANNEL_USERNAME = "@best_dealsareon"

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(__file__)

FRONTEND_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "../frontend")
)

JSON_FILE = os.path.join(
    FRONTEND_DIR,
    "deals.json"
)

IMAGES_DIR = os.path.join(
    FRONTEND_DIR,
    "images"
)

# =====================================================
# CREATE REQUIRED FOLDERS
# =====================================================

os.makedirs(IMAGES_DIR, exist_ok=True)

# =====================================================
# SAFE JSON LOAD
# =====================================================

deals = []

try:

    if not os.path.exists(JSON_FILE):

        with open(
            JSON_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            f.write("[]")

    with open(
        JSON_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        raw = f.read().strip()

        if raw == "":
            deals = []

        else:

            deals = json.loads(raw)

except Exception as e:

    print(f"⚠️ JSON FIXED: {e}")

    deals = []

    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("[]")

print("✅ JSON READY")

# =====================================================
# TELEGRAM CLIENT
# =====================================================

client = TelegramClient(
    StringSession(SESSION_STR),
    API_ID,
    API_HASH
)

# =====================================================
# PRICE EXTRACTION
# =====================================================

def extract_prices(text):

    prices = re.findall(
        r'(?:₹|Rs\.?|INR)\s?(\d+(?:,\d+)*)',
        text,
        flags=re.IGNORECASE
    )

    old_price = 0
    new_price = 0
    discount = "0% OFF"

    try:

        if len(prices) >= 2:

            p1 = int(prices[0].replace(",", ""))
            p2 = int(prices[1].replace(",", ""))

            old_price = max(p1, p2)
            new_price = min(p1, p2)

            if old_price > 0:

                disc = (
                    (old_price - new_price)
                    / old_price
                ) * 100

                discount = f"{round(disc)}% OFF"

        elif len(prices) == 1:

            new_price = int(
                prices[0].replace(",", "")
            )

            old_price = new_price

    except:
        pass

    return old_price, new_price, discount

# =====================================================
# STORE DETECTION
# =====================================================

def detect_store(text):

    lower = text.lower()

    if "amazon" in lower:
        return "Amazon"

    elif "flipkart" in lower:
        return "Flipkart"

    elif "myntra" in lower:
        return "Myntra"

    elif "ajio" in lower:
        return "Ajio"

    elif "nykaa" in lower:
        return "Nykaa"

    return "Store"

# =====================================================
# SAVE JSON
# =====================================================

def save_json():

    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            deals,
            f,
            ensure_ascii=False,
            indent=2
        )

# =====================================================
# MESSAGE HANDLER
# =====================================================

@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handler(event):

    try:

        text = event.message.message or ""

        if not text:
            return

        print("📩 New Telegram Deal")

        urls = re.findall(
            r'(https?://\\S+)',
            text
        )

        main_link = urls[0] if urls else "#"

        title = text.split("\\n")[0][:180]

        old_price, new_price, discount = (
            extract_prices(text)
        )

        store = detect_store(text)

        # =============================================
        # IMAGE DOWNLOAD
        # =============================================

        image_path = ""

        if event.photo:

            downloaded = await event.download_media()

            filename = os.path.basename(
                downloaded
            )

            final_path = os.path.join(
                IMAGES_DIR,
                filename
            )

            shutil.move(
                downloaded,
                final_path
            )

            image_path = f"images/{filename}"

            print("🖼 Image Saved")

        # =============================================
        # CREATE DEAL OBJECT
        # =============================================

        deal = {

            "id": event.id,

            "title": title,

            "caption": text,

            "image": image_path,

            "old_price": old_price,

            "new_price": new_price,

            "discount": discount,

            "main_link": main_link,

            "all_links": urls,

            "store": store
        }

        # =============================================
        # INSERT LATEST FIRST
        # =============================================

        deals.insert(0, deal)

        # =============================================
        # SAVE JSON
        # =============================================

        save_json()

        print("✅ Deal Saved")

    except Exception as e:

        print(f"❌ Handler Error: {e}")

# =====================================================
# MAIN
# =====================================================

async def main():

    print(f"🚀 Listening To {CHANNEL_USERNAME}")

    await client.start()

    print("✅ Telegram Connected")

    await client.run_until_disconnected()

# =====================================================

if __name__ == "__main__":

    asyncio.run(main())
