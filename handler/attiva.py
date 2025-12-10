from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler,MessageHandler,filters
from keyboards import getKeyboard_Bande,getKeyboard_Modi
from handler.call import cancel # TODO: Isolare cancel
import datetime
from config import BANDA,MODO,BANDE_DATA
from database.db import addAttivi,isAttivo, selectNominativo,getUtentiConcorrenti,selectNominativo

async def attivazioneStep_ONE(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """ Genero la keyboard con i nominativi e ritorno lo stato della conversazione """
    nominativo = selectNominativo(update.effective_user.id)

    # Se è negli utenti attivi lo avviso

    if nominativo is None:
        await update.message.reply_text(
            f"⚠️ Non risulti associato ad un nominativo YOTA \n esegui /call \n"
        ) 

        return ConversationHandler.END
    
    attivo = isAttivo(nominativo[1])
    print(attivo)

    if attivo is not None:
        await update.message.reply_text(
            f"⚠️ Risulti già attivo con il call {attivo[1]}.\n"
            "Usa /fine prima di ricominciare."
        )
        return ConversationHandler.END
    
    nominativo = selectNominativo(update.effective_user.id)
    context.user_data['temp_call'] = nominativo[2] # Nominativo speciale
    context.user_data['temp_operator'] = nominativo[1] # Nominativo personale
    await update.message.reply_text(
    f"✅ Operi come {nominativo[2]}\n🗣️Operatore: {nominativo[1]}\n"
    "Ora seleziona la Banda su cui trasmetterai:",
    reply_markup=getKeyboard_Bande() 
    )

    return BANDA # Passo all'acquisizione della banda

async def attivazioneStep_TWO(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Ricevo e controllo la banda """

    banda = update.message.text.strip()

    # Se la banda è sbagliata allora non proseguo con l'attivazione 
    if banda not in BANDE_DATA:
        await update.message.reply_text(
            f"⚠️ Errore: '{banda}' non valida.\n👇 Usa i pulsanti:",
            reply_markup=getKeyboard_Bande()
        )
        return BANDA
    
    # === Piu operatori possono operare sulla stessa banda MA con modo DIVERSO. ===
    occupati = getUtentiConcorrenti(context.user_data['temp_call'],banda)
    messaggio_avviso = ""
    if occupati:
        # Creiamo una lista formattata degli utenti già attivi
        lista_occupati = "\n".join(
            f"🗣️ {operatore} (Modo: {modo})" for modo, operatore in occupati
        )
        messaggio_avviso = (
            f"⚠️ Nota: Su {banda} sono già attivi i seguenti operatori:\n"
            f"{lista_occupati}\n"
            "Puoi comunque operare, ma scegli un modo diverso!\n\n"
        )



    # Salvo la banda in cui lavoro
    context.user_data['temp_banda'] = banda

    # Passo alla scelta del modo
    await update.message.reply_text(
        f"{messaggio_avviso}\n👍 Banda {banda} selezionata.\n"
        "Ora seleziona il Modo di Emissione:",
        reply_markup=getKeyboard_Modi()
    )

    return MODO
    
async def attivazioneStep_THREE(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Utlima fase della conversazione, legge la modalità di trasmissione controlla chi è ONLINE ed eventualmente esegue la query """

    modoScelto = update.message.text.strip()

    # Se Il modo è già occupato da un altro con stessa banda: BLOCCALO   
    occupati = getUtentiConcorrenti(context.user_data['temp_call'], context.user_data["temp_banda"])
    print(occupati)
    isOccupato = None
    operatorName = None

    for modo, operatore in occupati:
        if modoScelto == modo:
            isOccupato = modo
            operatorName = operatore
            break

    if isOccupato:
        markup_modi = getKeyboard_Modi()  # la tua funzione per rigenerare i pulsanti
        await update.message.reply_text(
            f"🛑 STOP! FREQUENZA OCCUPATA 🛑\n\n"
            f'Non puoi andare in {modoScelto} su {context.user_data["temp_banda"]}!\n'
            f"C'è già l'operatore: {operatorName}\n\n"
            "👇 Scegli un altro modo:",
            reply_markup=markup_modi
        )
        return MODO  

    
    # Inserimento dell'attivazione 
    addAttivi(context.user_data["temp_call"], context.user_data["temp_banda"], modoScelto, context.user_data["temp_operator"] ,datetime.datetime.now().strftime("%H:%M"))

    # Visualizzazione del messaggio
    await update.message.reply_text(
        f"✅ Attivazione Avviata!\n\n"
        f'🆔 Call: {context.user_data["temp_call"]}\n'
        f'〰️ Banda: {context.user_data["temp_banda"]}\n'
        f"🔊 Modo: {modoScelto}\n"
        f'👤 Op: {context.user_data["temp_operator"]}\n'
        f'🕒 Ora: {datetime.datetime.now().strftime("%H:%M")}\n\n'
        "Buon DX! /fine per chiudere.",
        reply_markup=ReplyKeyboardRemove()
    )

    # Eventuale messaggio broadcast

    return ConversationHandler.END


attiva = ConversationHandler(
    entry_points=[CommandHandler("attiva", attivazioneStep_ONE)],
    states={
        BANDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, attivazioneStep_TWO)],
        MODO: [MessageHandler(filters.TEXT & ~filters.COMMAND, attivazioneStep_THREE)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

def getAttiva()->ConversationHandler:
    return attiva