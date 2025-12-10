from telegram import Update,ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler,MessageHandler,filters
from config import SET_CALL,NOMINATIVI_SPECIALI
from database.db import getNominativi,addNominativo,selectNominativo,isAttivo


async def callState_ONE(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stato 1: L'utente scrive /call. Il bot chiede il nominativo."""

    # In questo stato della /call inserisco il nominativo

    # NON PUOI FARE /CALL SE SEI ATTIVO
    nominativo = selectNominativo(update.effective_user.id)
    print(nominativo)
    if nominativo:  # Ha già un nominativo registrato
        attivo = isAttivo(nominativo[1])  
        if attivo:
            await update.message.reply_text(
                f"⚠️ Risulti già attivo con il call {attivo[1]}.\n"
                "Usa /fine prima di ricominciare."
            )
            return ConversationHandler.END

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
    nominativi = getNominativi()

    # Validazione base: lunghezza
    if len(input_text) < 3 or len(input_text) > 10:
        print("TROPPO LUNGO")
        await update.message.reply_text("⚠️ Nominativo non valido (troppo corto o lungo). Riprova.")
        return SET_CALL # Rimaniamo in attesa finché non ne scrive uno giusto
    else: # Controllo eventuali duplicati
        for row in nominativi:
            print(row[1])
            if row[1] == input_text:
                await update.message.reply_text("⚠️ Esiste già un utente con questo nominativo. Riprova /call")
                return ConversationHandler.END


    # Assegno automaticamente il nominativo 
    numero = ''.join([c for c in input_text if c.isdigit()])
    team = None

    if numero:
        for n in NOMINATIVI_SPECIALI:
            if numero in n:
                team = n
                print(team)
                break

    if team is None:
        await update.message.reply_text("⚠️ Nominativo non associabile, contatta l'amministratore")
        return ConversationHandler.END
    else:
        try:
            print("INSERISCO NOMINATIVO")
            addNominativo(input_text, str(update.effective_user.id), str(team)) # Aggiungo il nominativo al database

            await update.message.reply_text(
                f"✅ Perfetto! {input_text} il tuo team di appartenenza è {team}\n"
            )
        except Exception as e:
            print(f"[ERRORE GENERICO] {e}") # *** Lancia questa exeption ***

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


