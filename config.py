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

NOMINATIVI = configData.get("nominativi",[])
BANDE = configData.get("bande",[])
MODI = configData.get("modi",[])

NOMINATIVO, BANDA, MODO, SET_CALL, RICEZIONE_LOG_CHIUSURA = range(5)


