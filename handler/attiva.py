from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler,MessageHandler,filters
from keyboards import getKeyboardNominativi,getKeyboard_Bande,getKeyboard_Modi
from handler.call import cancel # TODO: Isolare cancel
from config import NOMINATIVO,BANDA,MODO,MODI_DATA,NOMINATIVI_SPECIALI

async def attivazioneStep_ONE(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # SE è NEGLI UTENTI ATTIVI 
        # AVVISALO
    
    # Aquisisco la keyboard da keyboards.py

    """ Genero la keyboard con i nominativi e ritorno lo stato della conversazione """

    await update.message.reply_text(
        "Ok, iniziamo! 🎙️\n"
        "Seleziona il Nominativo con cui vuoi trasmettere:",
        reply_markup=getKeyboardNominativi()
    ) 
    return NOMINATIVO # Ora devo scegliere il nominativo

# Dopo aver scritto il nominativo
async def attivazioneStep_TWO(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """ Acquisisco il nominativo lo controllo e genero le bande """

    # Sicuramente lo devo acquisire quindi
    nominativo = update.message.text.upper().strip()

    # Controllo se esiste
        # Anche se da Mobile la tastiera è obbligatoria, ma in caso di Paste o TG WEB
    
    # Salvo il "nominativo"
    context.user_data['temp_call'] = nominativo


    await update.message.reply_text(
        f"✅ Operi come {nominativo}.\n"
        "Ora seleziona la Banda su cui trasmetterai:",
        reply_markup=getKeyboard_Bande() 
    )

    return BANDA # Ora devo scegliere la banda

async def attivazioneStep_THREE(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Ricevo e controllo la banda """

    banda = update.message.text.strip()

    # Se la banda non è valida
        # Ritorno a scrivere la banda
    
    # Controllo se è libera
        # E costruisco il messaggio di risposta se non è libera indicando CHI e COME

    # Salvo la banda in cui lavoro
    context.user_data['temp_banda'] = banda

    # Passo alla scelta del modo
    await update.message.reply_text(
        f"👍 Banda {banda} selezionata.\n"
        "Ora seleziona il Modo di Emissione:",
        reply_markup=getKeyboard_Modi()
    )

    return MODO
    


attiva = ConversationHandler(
    entry_points=[CommandHandler("attiva", attivazioneStep_ONE)],
    states={
        NOMINATIVO: [MessageHandler(filters.TEXT & ~filters.COMMAND, attivazioneStep_TWO)],
        BANDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, attivazioneStep_THREE)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

def getAttiva()->ConversationHandler:
    return attiva