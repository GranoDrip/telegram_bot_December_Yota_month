"""
bot.py

"""

from config import *

import logging
import os
import requests
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from database.db import initDatabase

from handler.start import getStart
from handler.regole import getRegole
from handler.call import getCall
from handler.cmds import getCmds # Comandi
from handler.attiva import getAttiva

# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO
# )

app = Application.builder().token(BOT_TOKEN).build()

initDatabase()
print("Inizializzazione del DB")

# Comandi principali
app.add_handler(getStart()) # START -- OK
app.add_handler(getRegole()) # REGOLE -- OK
app.add_handler(getCall()) # CALL -- OK -> INSERIRE NOMINATIVO NEL DB
app.add_handler(getAttiva()) # LISTA 
# FINE 
app.add_handler(getCmds()) # COMANDI - OK

# Avvio
if __name__ == "__main__":
    print("Avvio")
    app.run_polling()