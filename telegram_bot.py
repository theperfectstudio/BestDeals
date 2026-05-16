import asyncio
            store = "Myntra"

        elif "ajio" in lower:
            store = "Ajio"

        elif "nykaa" in lower:
            store = "Nykaa"

        # =================================================
        # DEAL OBJECT
        # =================================================

        deal = {
            "id": timestamp,
            "title": title,
            "caption": text,
            "image": image_path,
            "old_price": old_price,
            "new_price": new_price,
            "discount": discount,
            "main_link": main_link,
            "all_links": urls,
            "store": store,
            "date": timestamp
        }

        # =================================================
        # INSERT LATEST FIRST
        # =================================================

        deals.insert(0, deal)

        # =================================================
        # SAVE JSON
        # =================================================

        with open(JSON_FILE, "w", encoding="utf-8") as f:

            json.dump(
                deals,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("✅ JSON Updated")

        # =================================================
        # SAVE GOOGLE SHEET
        # =================================================

        sheet.append_row([
            timestamp,
            title,
            image_path,
            old_price,
            new_price,
            discount,
            main_link,
            store,
            text
        ])

        print("✅ Google Sheet Updated")

    except Exception as e:

        print(f"❌ Error: {e}")

# =====================================================
# MAIN
# =====================================================

async def main():

    print(f"🚀 Listening To {CHANNEL_USERNAME}")

    await client.start()

    print("✅ Telegram Connected")

    await client.run_until_disconnected()

if __name__ == "__main__":

    asyncio.run(main())
