from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler,MessageHandler,filters
from keyboards import getKeyboard_Bande,getKeyboard_Modi
from handler.call import cancel # TODO: Isolare cancel
import datetime
from config import BANDA,MODO,BANDE_DATA,NEW_BANDA,NEW_MODO
from database.db import addAttivi,isAttivo, selectNominativo,getUtentiConcorrenti,selectNominativo,updateAttivi

# Step 1: acquisizione della banda da modificare
async def modificaStep_ONE(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    nominativo = selectNominativo(update.effective_user.id)

    if nominativo is None:
        await update.message.reply_text(
        f"⚠️ Non risulti associato ad un nominativo YOTA \n esegui /call \n"
        ) 

        return ConversationHandler.END

    context.user_data['temp_operator'] = nominativo[1]
    context.user_data['temp_call'] = nominativo[2]

    attivo = isAttivo(nominativo[1])
    print(attivo)

    if attivo is None:
        await update.message.reply_text(
            f"⚠️ Non risulta nessuna attivazione\n"
            "Usa /attiva prima di modificare."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Seleziona la banda:",
        reply_markup=getKeyboard_Bande()
    )
    return NEW_BANDA

async def modificaStep_TWO(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Ricevo e modifico la banda """

    banda = update.message.text.strip()

    # Se la banda è sbagliata allora non proseguo con l'attivazione 
    if banda not in BANDE_DATA:
        await update.message.reply_text(
            f"⚠️ Errore: '{banda}' non valida.\n👇 Usa i pulsanti:",
            reply_markup=getKeyboard_Bande()
        )
        return NEW_BANDA
    
    occupati = getUtentiConcorrenti(context.user_data['temp_call'],banda)

    occupati = [t for t in occupati if t[1] != context.user_data['temp_operator']] # ESCLUDO ME STESSO

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
        "Ora seleziona il modo di Emissione:",
        reply_markup=getKeyboard_Modi()
    )

    return NEW_MODO

async def modificaStep_THREE(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Utlima fase della conversazione, legge la modalità di trasmissione, controlla chi è ONLINE ed eventualmente esegue la query """

    modoScelto = update.message.text.strip()

    # Se Il modo è già occupato da un altro con stessa banda: BLOCCALO
    occupati = getUtentiConcorrenti(context.user_data['temp_call'], context.user_data["temp_banda"])

    # Rimuovo il record del mio operatore dalla lista
    occupati = [t for t in occupati if t[1] != context.user_data['temp_operator']] # ESCLUDO ME

    isOccupato = None
    operatorName = None

    for modo, operatore in occupati:
        if modoScelto == modo:
            isOccupato = modo
            operatorName = operatore
            break

    if isOccupato:
        markup_modi = getKeyboard_Modi()  # rigenero i pulsanti dei modi
        await update.message.reply_text(
            f"🛑 STOP! FREQUENZA OCCUPATA 🛑\n\n"
            f"Non puoi andare in {modoScelto} su {context.user_data['temp_banda']}!\n"
            f"C'è già l'operatore: {operatorName}\n\n"
            "👇 Scegli un altro modo:",
            reply_markup=markup_modi
        )
        return NEW_MODO  

    # Inserimento dell'attivazione
    updateAttivi(
        context.user_data["temp_operator"],
        context.user_data["temp_banda"],
        modoScelto,
    )



    # Visualizzazione del messaggio
    await update.message.reply_text(
        f"✅ MODIFICA COMPLETATA!\n\n"
        f"🆔 Call: {context.user_data['temp_call']}\n"
        f"〰️ Banda: {context.user_data['temp_banda']}\n"
        f"🔊 Modo: {modoScelto}\n"
        f"👤 Op: {context.user_data['temp_operator']}\n"
        "\n"
        "Buon DX! /fine per chiudere.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END



modifica = ConversationHandler(
    entry_points=[CommandHandler("modifica", modificaStep_ONE)],
    states={
        NEW_BANDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, modificaStep_TWO)],
        NEW_MODO: [MessageHandler(filters.TEXT & ~filters.COMMAND, modificaStep_THREE)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


def getModfica()->ConversationHandler:
    return modifica