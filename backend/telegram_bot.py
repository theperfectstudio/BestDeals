# =====================================================
# FILE: backend/telegram_bot.py
# =====================================================

import asyncio
import os
import re
import json
import shutil

from telethon import TelegramClient
from telethon.sessions import StringSession

# =====================================================
# CONFIG
# =====================================================

API_ID = int(os.getenv("API_ID"))

API_HASH = os.getenv("API_HASH")

SESSION_STR = os.getenv("SESSION_STR")

CHANNEL_USERNAME = "@best_dealsareon"

MAX_POSTS = 20

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(__file__)

ROOT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

JSON_FILE = os.path.join(
    ROOT_DIR,
    "deals.json"
)

IMAGES_DIR = os.path.join(
    ROOT_DIR,
    "images"
)

# =====================================================
# CREATE FOLDERS
# =====================================================

os.makedirs(IMAGES_DIR, exist_ok=True)

# =====================================================
# LOAD EXISTING DEALS
# =====================================================

deals = []

try:

    if os.path.exists(JSON_FILE):

        with open(
            JSON_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            raw = f.read().strip()

            if raw:

                deals = json.loads(raw)

except Exception as e:

    print(
        f"⚠️ JSON ERROR: {e}",
        flush=True
    )

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

    return (
        old_price,
        new_price,
        discount
    )

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
# CATEGORY DETECTION
# =====================================================

def detect_category(text):

    lower = text.lower()

    if any(word in lower for word in [
        "mobile",
        "iphone",
        "samsung",
        "redmi",
        "realme",
        "vivo",
        "oppo"
    ]):
        return "Mobiles"

    elif any(word in lower for word in [
        "laptop",
        "macbook",
        "lenovo",
        "hp",
        "dell"
    ]):
        return "Laptops"

    elif any(word in lower for word in [
        "shirt",
        "shoe",
        "jeans",
        "kurta",
        "fashion"
    ]):
        return "Fashion"

    elif any(word in lower for word in [
        "watch",
        "boat",
        "earbuds",
        "headphone"
    ]):
        return "Electronics"

    return "Other"

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
# MAIN
# =====================================================

async def main():

    print(
        "🚀 FETCHING TELEGRAM POSTS...",
        flush=True
    )

    await client.start()

    print(
        "✅ TELEGRAM CONNECTED",
        flush=True
    )

    existing_links = {

        deal.get("main_link", "")

        for deal in deals
    }

    new_count = 0

    async for message in client.iter_messages(
        CHANNEL_USERNAME,
        limit=MAX_POSTS
    ):

        try:

            text = message.message or ""

            if not text:

                continue

            urls = re.findall(
                r'(https?://\S+)',
                text
            )

            main_link = (
                urls[0]
                if urls
                else "#"
            )

            # =========================================
            # SKIP DUPLICATE
            # =========================================

            if main_link in existing_links:

                print(
                    "⚠️ DUPLICATE SKIPPED",
                    flush=True
                )

                continue

            print(
                f"📩 NEW DEAL: {message.id}",
                flush=True
            )

            title = text.split("\n")[0][:180]

            (
                old_price,
                new_price,
                discount
            ) = extract_prices(text)

            store = detect_store(text)

            category = detect_category(text)

            # =========================================
            # DOWNLOAD IMAGE
            # =========================================

            image_path = ""

            if message.photo:

                downloaded = (
                    await message.download_media()
                )

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

                image_path = (
                    f"images/{filename}"
                )

                print(
                    "🖼 IMAGE SAVED",
                    flush=True
                )

            # =========================================
            # CREATE DEAL
            # =========================================

            deal = {

                "id": message.id,

                "title": title,

                "caption": text,

                "image": image_path,

                "old_price": old_price,

                "new_price": new_price,

                "discount": discount,

                "main_link": main_link,

                "all_links": urls,

                "store": store,

                "category": category
            }

            deals.insert(0, deal)

            existing_links.add(main_link)

            new_count += 1

        except Exception as e:

            print(
                f"❌ POST ERROR: {e}",
                flush=True
            )

    # =================================================
    # SAVE JSON
    # =================================================

    save_json()

    print(
        f"✅ {new_count} NEW DEALS ADDED",
        flush=True
    )

    await client.disconnect()

# =====================================================
# START
# =====================================================

if __name__ == "__main__":

    asyncio.run(main())
