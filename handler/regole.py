from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler

async def regole(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra le regole di utilizzo del bot."""
    await update.message.reply_text(
        "📜 Regole per l'uso del Bot di Attivazione Radio del DYM 2025 📜\n\n"
        "1. Usa il comando /call per inserire il tuo nominativo personale. (consigliato!)n"
        "2. Usa il comando /attiva per iniziare una nuova attivazione.\n"
        "3. Seleziona il tuo nominativo dalla lista proposta.\n"
        "4. Fornisci la frequenza su cui opererai.\n"
        "5. Per vedere chi è attivo, usa il comando /lista.\n"
        "6. Quando hai finito, usa il comando /fine per terminare l'attivazione e caricare i log.\n"
        "7. Usa il comando /notifiche per attivare o disattivare le notifiche (in arrivo).\n\n"
        "⚠️ Assicurati di non avere attivazioni multiple aperte contemporaneamente.\n"
        "Buon divertimento e buoni collegamenti! 📡"
    )
    await update.message.reply_text(
        f"Comandi disponibili:\n"
        "📜 /regole - Mostra le regole\n"
        "🔔 /notifiche - Gestisci le notifiche (in arrivo)\n"
        "🆔 /call - Aggiungi il tuo nominativo personale\n"
        "📡 /attiva - Inizia una nuova attivazione\n"
        "📝 /lista - Vedi chi è attualmente in frequenza\n"
        "🛑 /fine - Termina la tua attivazione corrente\n"
        "⚙️ /comandi - Lista dei comandi disponibili\n"
    )
    return ConversationHandler.END

def getRegole() -> CommandHandler:
    return CommandHandler("regole", regole)