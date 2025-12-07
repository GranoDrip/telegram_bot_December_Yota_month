from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Messaggio di benvenuto."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    await update.message.reply_text(
        f"Ciao {user.full_name}! 👋\n"
        "Sono il bot per la gestione delle attivazioni radio per il DYM 2025.\n\n"
        "Prima di iniziare a lavorare usa il comando /regole per sapere tutto sul funzinamento. \n\n"
        "Comandi disponibili:\n"
        "📜 /regole - Mostra le regole\n"
        "🔔 /notifiche - Gestisci le notifiche (in arrivo)\n"
        "🆔 /call - Aggiungi il tuo nominativo personale\n"
        "📡 /attiva - Inizia una nuova attivazione\n"
        "📝 /lista - Vedi chi è attualmente in frequenza\n"
        "🛑 /fine - Termina la tua attivazione corrente\n"
        "⚙️ /comandi - Lista dei comandi disponibili\n"
    )
    return ConversationHandler.END

def getStart() -> CommandHandler:
    return CommandHandler("start", start)