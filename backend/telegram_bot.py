# =====================================================
# FILE: backend/telegram_bot.py
# AI CLEAN + DYNAMIC DEAL GENERATOR
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

MAX_POSTS = 25

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
# CREATE DIRS
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

    print(f"⚠️ JSON ERROR: {e}")

    deals = []

# =====================================================
# TELEGRAM
# =====================================================

client = TelegramClient(
    StringSession(SESSION_STR),
    API_ID,
    API_HASH
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

    elif "boat" in lower:
        return "Boat"

    return "Trending"

# =====================================================
# CATEGORY
# =====================================================

def detect_category(text):

    lower = text.lower()

    if any(x in lower for x in [
        "iphone",
        "samsung",
        "realme",
        "redmi",
        "mobile"
    ]):
        return "Mobiles"

    elif any(x in lower for x in [
        "laptop",
        "macbook",
        "hp",
        "dell"
    ]):
        return "Laptops"

    elif any(x in lower for x in [
        "shoe",
        "shirt",
        "fashion"
    ]):
        return "Fashion"

    elif any(x in lower for x in [
        "earbuds",
        "watch",
        "speaker"
    ]):
        return "Electronics"

    return "Other"

# =====================================================
# AI CLEAN CAPTION
# =====================================================

def clean_caption(text):

    lines = text.split("\n")

    cleaned = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # REMOVE TELEGRAM LINKS

        if "t.me/" in line:
            continue

        cleaned.append(line)

    return "\n".join(cleaned[:12])

# =====================================================
# TITLE
# =====================================================

def generate_title(text):

    lines = text.split("\n")

    title = lines[0][:120]

    title = title.replace("🔥","")

    return title.strip()

# =====================================================
# LOAD EXISTING LINKS
# =====================================================

existing_links = {

    d.get("main_link","")

    for d in deals
}

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

    print("🚀 FETCHING DEALS...")

    await client.start()

    print("✅ TELEGRAM CONNECTED")

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

            if not urls:
                continue

            main_link = urls[0]

            # DUPLICATE

            if main_link in existing_links:

                print("⚠️ DUPLICATE")

                continue

            print(f"📩 NEW DEAL {message.id}")

            # IMAGE

            image_path = ""

            if message.photo:

                try:

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

                    print("🖼 IMAGE SAVED")

                except Exception as e:

                    print(f"⚠️ IMAGE ERROR: {e}")

            # DATA

            cleaned_caption = clean_caption(text)

            title = generate_title(text)

            category = detect_category(text)

            store = detect_store(text)

            # SAVE

            deal = {

                "id": message.id,

                "title": title,

                "caption": cleaned_caption,

                "image": image_path,

                "main_link": main_link,

                "all_links": urls,

                "category": category,

                "store": store
            }

            deals.insert(0, deal)

            existing_links.add(main_link)

            new_count += 1

        except Exception as e:

            print(f"❌ ERROR: {e}")

    # LIMIT

    deals[:] = deals[:100]

    save_json()

    print(f"✅ {new_count} NEW DEALS ADDED")

    await client.disconnect()

# =====================================================

if __name__ == "__main__":

    asyncio.run(main())