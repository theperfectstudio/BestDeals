import asyncio

print("✅ NEW FILE RUNNING")

async def main():

    print("🚀 BOT STARTED")

    while True:

        await asyncio.sleep(10)

if __name__ == "__main__":

    asyncio.run(main())
