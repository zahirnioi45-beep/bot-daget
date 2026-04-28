import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN       = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID") or 0)
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/kepoqnjieng")
OWNER_ID   = int(os.getenv("OWNER_ID") or 0)
OWNER_USERNAME  = os.getenv("OWNER_USERNAME")
BOT_USERNAME    = os.getenv("BOT_USERNAME")

TEMPLATES = {
    1: {
        "name": "🔴 TEMPLATE MERAH",
        "desc": "Gaya agresif - cocok buat promo hot",
        "emoji": "🔴"
    },
    2: {
        "name": "🟡 TEMPLATE KUNING",
        "desc": "Gaya santai - cocok buat sharing",
        "emoji": "🟡"
    },
    3: {
        "name": "🟢 TEMPLATE HIJAU",
        "desc": "Gaya profesional - cocok buat bisnis",
        "emoji": "🟢"
    },
}

MESSAGES = [
    "💸 BAGI BAGI LAGI BOSKU GAUSAH DI SEMBAH YA!",
    "🔥 MAAF RECEH SOALNYA GAMAU DI SEMBAH WKWKW!",
    "⚡ ALERGI PERAKAN APALAGI 5P KEK SEBELAH!",
    "🎯 LAGI ADA REZEKI OENGEN BAGI BAGI DIKIT GAUSAH DI PUJI!",
    "🚀 DAGI BAGI LAGI BAE GW INI WKWKWKW!",
]

COOLDOWN_SECONDS = 2
