from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler
from config import CMDS

async def cmds(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra la lista dei comandi disponibili."""
    await update.message.reply_text(
        f"""{CMDS}"""
    )
    return ConversationHandler.END

def getCmds() -> ConversationHandler:
    return CommandHandler("comandi", cmds)