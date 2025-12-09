from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler,MessageHandler,filters
from keyboards import getKeyboardNominativi,getKeyboard_Bande,getKeyboard_Modi
from handler.call import cancel # TODO: Isolare cancel
import datetime
from config import NOMINATIVO,BANDA,MODO,MODI_DATA,NOMINATIVI_SPECIALI,BANDE_DATA
from database.db import getAttivi,addAttivi,isAttivo

async def attivazioneStep_ONE(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """ Genero la keyboard con i nominativi e ritorno lo stato della conversazione """

    # Se è negli utenti attivi lo avviso
    attivo = isAttivo(update.effective_user.first_name)

    if attivo is not None:
        await update.message.reply_text(
            f"⚠️ Risulti già attivo con il call {attivo[1]}.\n"
            "Usa /fine prima di ricominciare."
        )
        return ConversationHandler.END

    # Aquisisco la keyboard da keyboards.py

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
    if nominativo not in NOMINATIVI_SPECIALI:
        await update.message.reply_text(
            f"⚠️ Questo nominativo non risulta registrato: {nominativo}.\n"
            "Scegline uno dalla tastiera!"
        )
        return NOMINATIVO

    
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

    # Se la banda è sbagliata allora non proseguo con l'attivazione 
    if banda not in BANDE_DATA:
        await update.message.reply_text(
            f"⚠️ Errore: '{banda}' non valida.\n👇 Usa i pulsanti:",
            reply_markup=getKeyboard_Bande()
        )
        return BANDA
    
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
    
async def attivazioneStep_FOUR(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Utlima fase della conversazione, legge la modalità di trasmissione controlla chi è ONLINE ed eventualmente esegue la query """

    modo = update.message.text.strip()

    # Controlla gli altri in call
        # Se è occupata allora cambia     
    
    # Inserimento dell'attivazione 
    addAttivi(context.user_data["temp_call"], context.user_data["temp_banda"], modo, update.effective_user.first_name ,datetime.datetime.now().strftime("%H:%M"))

    # Visualizzazione del messaggio
    await update.message.reply_text(
        f"✅ Attivazione Avviata!\n\n"
        f"🆔 Call: {context.user_data["temp_call"]}\n"
        f"〰️ Banda: {context.user_data["temp_banda"]}\n"
        f"🔊 Modo: {modo}\n"
        f"👤 Op: {update.effective_user.first_name}\n"
        f"🕒 Ora: {datetime.datetime.now().strftime("%H:%M")}\n\n"
        "Buon DX! /fine per chiudere.",
        reply_markup=ReplyKeyboardRemove()
    )

    # Eventuale messaggio broadcast

    return ConversationHandler.END


attiva = ConversationHandler(
    entry_points=[CommandHandler("attiva", attivazioneStep_ONE)],
    states={
        NOMINATIVO: [MessageHandler(filters.TEXT & ~filters.COMMAND, attivazioneStep_TWO)],
        BANDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, attivazioneStep_THREE)],
        MODO: [MessageHandler(filters.TEXT & ~filters.COMMAND, attivazioneStep_FOUR)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

def getAttiva()->ConversationHandler:
    return attiva