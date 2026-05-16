from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# તમારી વિગતો અહીં નાખો
API_ID = '35795778'
API_HASH = 'd4256dd43d5184feed3f3680e5f3812f'

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    session_str = client.session.save()
    print("\n--- તમારી SESSION STRING નીચે મુજબ છે ---")
    print(session_str)
    print("--- આને કોપી કરીને સુરક્ષિત રાખો ---")