from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler
from config import CMDS

async def regole(update: Update,context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra le regole di utilizzo del bot."""
    await update.message.reply_text(
        "📜 Regole per l'uso del Bot di Attivazione Radio del DYM 2025 📜\n\n"
        "1. Puoi modificare il tuo nominativo usando il comando /call.\n"
        "2. Usa il comando /attiva per iniziare una nuova attivazione.\n"
        "3. Fornisci la frequenza su cui opererai.\n"
        "4. Usa il comando /cancel per annullare l'operazione.\n"
        "5. Per vedere chi è attivo, usa il comando /lista.\n"
        "6. Puoi usare /fine per terminare l'attivazione ed inviare il file log\n"
        "7. Per modificare la tua attuale attivazione, usa /modifica\n"
        "8. In caso di necessità puoi caricare SOLO il log usando /caricalog \n"
        "9. Usa il comando /notifiche per attivare o disattivare le notifiche (in arrivo).\n\n"
        "⚠️ Assicurati di non avere attivazioni multiple aperte contemporaneamente.\n"
        "Buon divertimento e buoni collegamenti! 📡"
    )

    # Messaggio con la lista di comandi
    await update.message.reply_text(
        f"""{CMDS}"""
    )


    return ConversationHandler.END

def getRegole() -> CommandHandler:
    return CommandHandler("regole", regole)