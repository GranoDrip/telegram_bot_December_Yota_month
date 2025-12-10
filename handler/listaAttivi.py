from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler,MessageHandler,filters
from database.db import getAttivi,addAttivi,isAttivo

async def attivi(update: Update, context: ContextTypes.DEFAULT_TYPE):

    attivi = getAttivi()
    print(attivi)

    messaggio = "🔇 Al momento non c'è nessuno in frequenza."

    if attivi:
        messaggio = ""
        for r in attivi:
            messaggio += (
            f"🗣️ {r[1]} (Op. {r[4]})\n"
            f"〰️ Banda: {r[2]} \n"
            f"🔊 Modo: {r[3]}\n"
            f"🕒 Dalle: {r[5]}\n"
            f"------------------\n"
        )
            
    await update.message.reply_text(messaggio)

    return ConversationHandler.END


def printAttivi():
    return CommandHandler("lista", attivi)

