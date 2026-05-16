import asyncio
import json
import os

JSON_FILE = "frontend/deals.json"

# =====================================================
# SAFE JSON LOAD
# =====================================================

deals = []

try:

    # create file if missing
    if not os.path.exists(JSON_FILE):

        os.makedirs("frontend", exist_ok=True)

        with open(JSON_FILE, "w", encoding="utf-8") as f:

            f.write("[]")

    # read safely
    with open(JSON_FILE, "r", encoding="utf-8") as f:

        raw = f.read().strip()

        if raw == "":
            deals = []
        else:
            deals = json.loads(raw)

except Exception as e:

    print("⚠️ JSON FIX APPLIED")
    print(e)

    deals = []

    with open(JSON_FILE, "w", encoding="utf-8") as f:

        f.write("[]")

print("✅ JSON WORKING")
print(deals)

# =====================================================

async def main():

    print("🚀 BOT RUNNING")

    while True:

        await asyncio.sleep(10)

# =====================================================

if __name__ == "__main__":

    asyncio.run(main())
