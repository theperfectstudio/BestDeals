# =====================================================
# DEALVERSE AI BOT
# WITH EARNKARO AUTO CONVERT
# =====================================================

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

import os
import re
import json
import requests
import asyncio

# =====================================================
# TELEGRAM
# =====================================================

API_ID = os.getenv("API_ID")

API_HASH = os.getenv("API_HASH")

SESSION_STR = os.getenv("SESSION_STR")

CHANNEL = "best_dealsareon"

# =====================================================
# EARNKARO
# =====================================================

EARNKARO_TOKEN = os.getenv(
    "EARNKARO_TOKEN"
)

# =====================================================
# FILES
# =====================================================

DEALS_FILE = "deals.json"

IMAGES_DIR = "images"

os.makedirs(
    IMAGES_DIR,
    exist_ok=True
)

# =====================================================
# LOAD OLD DEALS
# =====================================================

try:

    with open(
        DEALS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        deals = json.load(f)

except:

    deals = []

# =====================================================
# EXISTING IDS
# =====================================================

existing_ids = [

    deal.get("message_id")

    for deal in deals
]

# =====================================================
# CLIENT
# =====================================================

client = TelegramClient(

    StringSession(SESSION_STR),

    API_ID,

    API_HASH
)

# =====================================================
# EARNKARO CONVERT
# =====================================================

def convert_to_earnkaro(url):

    try:

        response = requests.post(

            "https://webapi.earnkaro.com/api/affiliate/link-converter",

            headers={

                "Authorization":
                f"Bearer {EARNKARO_TOKEN}",

                "Content-Type":
                "application/json"
            },

            json={
                "url":url
            },

            timeout=20
        )

        data = response.json()

        print("EARNKARO:",data)

        if(

            "data" in data

            and

            "shortUrl" in data["data"]

        ):

            return data["data"]["shortUrl"]

        return url

    except Exception as e:

        print(
            "EARNKARO ERROR:",
            e
        )

        return url

# =====================================================
# CATEGORY DETECT
# =====================================================

def detect_category(text):

    text = text.lower()

    if any(

        word in text

        for word in [

            "iphone",
            "mobile",
            "phone",
            "samsung",
            "redmi",
            "realme"
        ]
    ):

        return "Mobiles"

    elif any(

        word in text

        for word in [

            "laptop",
            "macbook",
            "hp",
            "dell"
        ]
    ):

        return "Laptops"

    elif any(

        word in text

        for word in [

            "shoe",
            "shirt",
            "fashion",
            "kurta"
        ]
    ):

        return "Fashion"

    elif any(

        word in text

        for word in [

            "earbuds",
            "speaker",
            "tv",
            "watch"
        ]
    ):

        return "Electronics"

    return "Other"

# =====================================================
# STORE DETECT
# =====================================================

def detect_store(url):

    url = url.lower()

    if "amazon" in url:

        return "Amazon"

    elif "flipkart" in url:

        return "Flipkart"

    elif "myntra" in url:

        return "Myntra"

    elif "ajio" in url:

        return "Ajio"

    return "Store"

# =====================================================
# MAIN
# =====================================================

async def main():

    # =============================================
    # START CLIENT
    # =============================================

    await client.start()

    print("TELEGRAM CONNECTED")

    # =============================================
    # FETCH MESSAGES
    # =============================================

    messages = await client.get_messages(

        CHANNEL,

        limit=20
    )

    new_deals = deals.copy()

    # =============================================
    # LOOP
    # =============================================

    for msg in messages:

        if msg.id in existing_ids:

            continue

        text = msg.message or ""

        if not text:

            continue

        print(
            "NEW MESSAGE:",
            msg.id
        )

        # =========================================
        # URL EXTRACT
        # =========================================

        urls = re.findall(

            r'https?://\S+',

            text
        )

        if not urls:

            continue

        # =========================================
        # TITLE
        # =========================================

        lines = text.split("\n")

        title = lines[0][:120]

        # =========================================
        # IMAGE
        # =========================================

        image_path = ""

        if msg.photo:

            file_path = await msg.download_media(

                file=IMAGES_DIR
            )

            image_path = file_path

        # =========================================
        # AFFILIATE LINKS
        # =========================================

        affiliate_links = []

        for url in urls:

            earn_link = convert_to_earnkaro(
                url
            )

            affiliate_links.append(
                earn_link
            )

        # =========================================
        # SEARCH LINKS
        # =========================================

        amazon_search = (

            "https://www.amazon.in/s?k="

            +

            requests.utils.quote(title)
        )

        flipkart_search = (

            "https://www.flipkart.com/search?q="

            +

            requests.utils.quote(title)
        )

        google_search = (

            "https://www.google.com/search?q="

            +

            requests.utils.quote(title)
        )

        # =========================================
        # CONVERT SEARCH LINKS
        # =========================================

        amazon_search_aff = convert_to_earnkaro(
            amazon_search
        )

        flipkart_search_aff = convert_to_earnkaro(
            flipkart_search
        )

        google_search_aff = convert_to_earnkaro(
            google_search
        )

        # =========================================
        # STORE
        # =========================================

        store = detect_store(
            urls[0]
        )

        # =========================================
        # CATEGORY
        # =========================================

        category = detect_category(
            text
        )

        # =========================================
        # SAVE DEAL
        # =========================================

        deal = {

            "message_id":msg.id,

            "title":title,

            "caption":text,

            "image":image_path,

            "category":category,

            "store":store,

            "all_links":affiliate_links,

            "amazon_search":
            amazon_search_aff,

            "flipkart_search":
            flipkart_search_aff,

            "google_search":
            google_search_aff
        }

        new_deals.insert(
            0,
            deal
        )

        print(
            "DEAL SAVED:",
            title
        )

    # =============================================
    # SAVE JSON
    # =============================================

    with open(

        DEALS_FILE,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            new_deals,

            f,

            ensure_ascii=False,

            indent=2
        )

    print("DEALS UPDATED")

    # =============================================
    # DISCONNECT
    # =============================================

    await client.disconnect()

# =====================================================
# RUN
# =====================================================

asyncio.run(main())