import time
import re
import os
import json
import gspread
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from oauth2client.service_account import ServiceAccountCredentials

# --- ૧. GitHub Secrets માંથી ડેટા મેળવવો ---
API_ID = int(os.getenv('API_ID', '35795778'))
API_HASH = os.getenv('API_HASH', 'd4256dd43d5184feed3f3680e5f3812f')
SESSION_STR = os.getenv('SESSION_STR')
CREDENTIALS_JSON = os.getenv('CREDENTIALS_JSON')
CHANNEL_USERNAME = '@best_dealsareon' 
SHEET_NAME = "EarnKaro_Deals"

# --- ૨. ગૂગલ શીટ કનેક્શન ---
def connect_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = json.loads(CREDENTIALS_JSON)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        print(f"❌ Sheet Error: {e}")
        return None

# --- ૩. કિંમતો અને ડિસ્કાઉન્ટ ગણવાનું ફંક્શન ---
def extract_prices_and_discount(text):
    prices = re.findall(r'(?:₹|Rs\.?|INR)\s?(\d+(?:,\d+)*)', text)
    old_price, new_price, discount_text = 0, 0, "0%"
    
    if len(prices) >= 2:
        p1 = int(prices[0].replace(',', ''))
        p2 = int(prices[1].replace(',', ''))
        old_price, new_price = max(p1, p2), min(p1, p2)
        if old_price > 0:
            discount_val = ((old_price - new_price) / old_price) * 100
            discount_text = f"{round(discount_val)}%"
    elif len(prices) == 1:
        new_price = int(prices[0].replace(',', ''))
        old_price = new_price
        
    return old_price, new_price, discount_text

# --- ૪. ટેલિગ્રામ ક્લાયન્ટ સેટઅપ (StringSession) ---
client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handler(event):
    msg_text = event.message.message
    if not msg_text: return

    print(f"\n📩 નવી પોસ્ટ એનાલિસિસ...")
    urls = re.findall(r'(https?://\S+)', msg_text)
    
    if urls:
        profit_link = urls[0]
        image_url = urls[1] if len(urls) > 1 else "No Image URL Found"
        title = msg_text.split('\n')[0][:100]
        old_p, new_p, discount = extract_prices_and_discount(msg_text)
        
        sheet = connect_sheet()
        if sheet:
            try:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([timestamp, title, image_url, old_p, new_p, discount, profit_link])
                print(f"✅ સેવ થયું: {title}")
            except Exception as e:
                print(f"❌ Sheet Update Error: {e}")

# --- ૫. રન (Always Live Infinite Loop) ---
async def main():
    print(f"🚀 GitHub Action Bot Started & Listening to {CHANNEL_USERNAME}...")
    # ક્લાયન્ટ કનેક્ટ કરો
    await client.start()
    
    # જ્યાં સુધી મેન્યુઅલી બંધ ન થાય ત્યાં સુધી લૂપ ચાલુ રાખશે
    while True:
        await time.sleep(10) # દર ૧૦ સેકન્ડે કનેક્શન જીવંત રાખશે

with client:
    client.loop.run_until_complete(main())
