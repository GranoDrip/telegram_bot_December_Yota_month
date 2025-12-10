from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler
from config import CMDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Messaggio di benvenuto."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    await update.message.reply_text(
        f"""Ciao {user.full_name}! 👋\nSono il bot per la gestione delle attivazioni radio per il DYM 2025.\n\nPrima di iniziare a lavorare usa il comando /regole per sapere tutto sul funzionamento. \n\n{CMDS}"""    
    )
    return ConversationHandler.END



def getStart() -> CommandHandler:
    return CommandHandler("start", start)