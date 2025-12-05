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

from handler.start import start

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

# Avvio
if __name__ == "__main__":
    print("Avvio")
    app.run_polling()