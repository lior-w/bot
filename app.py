import os
import logging
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Read from env vars (set in Render dashboard)
TOKEN: Final = os.getenv("BOT_TOKEN")  # e.g. 8448:xxxx
BOT_USERNAME: Final = os.getenv("BOT_USERNAME", "@TikTokUrl2025Bot")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello")

def handle_response(text: str) -> str:
    return "this is a test response"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_type = update.message.chat.type
    text = update.message.text or ""
    logger.info('User (%s) in %s: "%s"', update.message.chat.id, message_type, text)
    response = handle_response(text)
    logger.info("Bot: %s", response)
    await update.message.reply_text(response)

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Update %s caused error: %s", update, context.error)

def main() -> None:
    logger.info("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # FIX: use add_handler (you had app.app_handler)
    app.add_handler(CommandHandler("start", start_command))

    # Echo normal text but ignore commands so /start isn’t echoed by MessageHandler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.add_error_handler(on_error)

    logger.info("Polling...")
    app.run_polling(poll_interval=3)

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN env var is missing")
    main()
