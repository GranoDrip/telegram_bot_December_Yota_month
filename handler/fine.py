from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler,MessageHandler,filters
from config import RICEZIONE_LOG_CHIUSURA,LOG_CHANNEL_ID
from database.db import selectNominativo,isAttivo,getAttivi,addStorico,removeAttivo
from handler.sendLog_utils import checkFileExention
from datetime import datetime
from handler.call import cancel

""" Gestiamo la fine della trasmissione inserendo nel DB i dati e se è stato inviato un log, cancelliamo la row attivi """

async def fineAttivazione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    nominativo = selectNominativo(update.effective_user.id)
    context.user_data["temp_nominativo"] = nominativo
    attivo = isAttivo(nominativo[1])

    if attivo is None:
        await update.message.reply_text("Non risulti attivo")
        return ConversationHandler.END

    # Chiudo senza log
    noLogKeyboard = ReplyKeyboardMarkup([["Chiudi senza Log"]], resize_keyboard=True, one_time_keyboard=True) 

    await update.message.reply_text(
        f"🛑 Richiesta di Chiusura per {nominativo[2]}\n\n"
        "Per terminare l'attività e liberare la frequenza, **devi caricare il log**.\n"
        "📂 Invia ora il file .ADI o .ADIF qui in chat.",
        reply_markup=noLogKeyboard,
        parse_mode="Markdown"
    )

    return RICEZIONE_LOG_CHIUSURA

# Mando il log attraverso l'API
async def sendLog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    attivazone = getAttivi(context.user_data["temp_nominativo"][1])

    if update.message.text.upper() == "Chiudi senza log".upper():
        addStorico(attivazone[1],attivazone[2],attivazone[3],attivazone[4],attivazone[5],datetime.now().strftime("%H:%M"))
        removeAttivo(context.user_data["temp_nominativo"][1])
        await update.message.reply_text(
            f"⚠️ Attività chiusa SENZA caricare il log.\nRicordati di caricarlo a mano!",
            reply_markup=ReplyKeyboardRemove()
        )
        # await context.bot.send_message(
        #     # chat_id=LOG_CHANNEL_ID, # MANDO AL CANALE DI LOG
        #     chat_id=update.effective_chat.id, # MANDO AL CANALE DI LOG
        #     text=f"⚠️ AVVISO: {attivazone[4]} ha chiuso {attivazone[1]} SENZA inviare il log."
        # )
        return ConversationHandler.END
    
    # ==== GESTIONE DEL FILE LOG ====

    document = update.message.document
    if not document:
        await update.message.reply_text("Devi inviare un file o premere 'Chiudi senza Log'.")
        return RICEZIONE_LOG_CHIUSURA
    
    if not checkFileExention(document.file_name):
        await update.message.reply_text("⚠️ Il file deve essere .adi o .adif!")
        return RICEZIONE_LOG_CHIUSURA
    
    await update.message.reply_text("⏳ File ricevuto. Elaborazione e chiusura...")

    # === GESTIONE API ===

fine = ConversationHandler(
    entry_points=[CommandHandler("fine", fineAttivazione)],
    states={
        RICEZIONE_LOG_CHIUSURA: [
            MessageHandler(filters.Document.ALL, sendLog),
            MessageHandler(filters.Regex("^Chiudi senza Log$"), sendLog)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

def getFine()->ConversationHandler:
    return fine