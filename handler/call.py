from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler,MessageHandler,filters
from config import SET_CALL

from database.db import getNominativi,addNominativo

async def callState_ONE(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # In questo stato della /call inserisco il nominativo

    """Stato 1: L'utente scrive /call. Il bot chiede il nominativo."""
    await update.message.reply_text(
        "🆔 Impostazione Call Personale\n\n"
        "Per favore, scrivi ora il tuo Nominativo (es. IU3XYZ).\n"
        "Lo userò per identificarti nelle liste.",
        parse_mode="Markdown"
    )
    return SET_CALL


async def callState_TWO(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fase 2: L'utente ha scritto il nominativo. Lo salviamo."""
    user_id = update.effective_user.id
    input_text = update.message.text.upper().strip() # TRASFORMO TUTTI IN MAIUSCOLO E TOLGO GLI SPAZI
    
    # Validazione base: lunghezza
    if len(input_text) < 3 or len(input_text) > 10:
        await update.message.reply_text("⚠️ Nominativo non valido (troppo corto o lungo). Riprova.")
        return SET_CALL # Rimaniamo in attesa finché non ne scrive uno giusto

    addNominativo(input_text)

    nominativi = getNominativi()

    if nominativi:
        strng = "\n".join(f"{nominativo}" for nominativo in nominativi)

    # TODO: INSERIRE IL NOMINATIVO NEL DATABASE
    await update.message.reply_text(str(nominativi))
    
    await update.message.reply_text(
        f"✅ Perfetto!\n"
        f"Registrazione di {input_text} effettuata con successo.\n"
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

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Permette di annullare l'operazione se l'utente cambia idea."""
    await update.message.reply_text("Operazione annullata.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Gestore conversazione per /call
call = ConversationHandler(
    entry_points=[CommandHandler("call", callState_ONE)],
    states={
        SET_CALL: [MessageHandler(filters.TEXT & ~filters.COMMAND, callState_TWO)], # Solo messaggi testuali e non comandi
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

def getCall() -> ConversationHandler:
    return call


