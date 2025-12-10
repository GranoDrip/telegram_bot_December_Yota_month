"""
config.py

Contiene tutte le configurazioni principali del bot, incluse:

Variabili d'ambiente (TOKEN Telegram, ID canale, API key YOTA)

Stati della conversazione

Liste dinamiche caricate da un JSON (nominativi, bande, modi)

Semplificando le operazioni di configurazione
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

# Setup 
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
YOTA_API_KEY = os.getenv("YOTA_API_KEY")

# Caricamento delle liste
with open("config_data.json",'r') as cf:
    configData = dict(json.load(cf))

NOMINATIVI_SPECIALI = configData.get("nominativi",[])
BANDE_DATA = configData.get("bande",[])
MODI_DATA = configData.get("modi",[])

NOMINATIVO, BANDA, NEW_BANDA, MODO ,NEW_MODO, SET_CALL, SET_TEAM , RICEZIONE_LOG_CHIUSURA = range(8)

CMDS = (
    "Comandi disponibili:\n"
    "📜 /regole - Mostra le regole\n"
    "🔔 /notifiche - Gestisci le notifiche (in arrivo)\n"
    "🆔 /call - Aggiungi il tuo nominativo personale\n"
    "📡 /attiva - Inizia una nuova attivazione\n"
    "🛠️ /modifica - Inizia una nuova attivazione\n"
    "📝 /lista - Vedi chi è attualmente in frequenza\n"
    "🛑 /fine - Termina la tua attivazione corrente\n"
    "⚙️ /comandi - Lista dei comandi disponibili\n"
)
