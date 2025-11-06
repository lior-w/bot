import os
import logging
from typing import Final
from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import Application

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN: Final = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET: Final = os.getenv("WEBHOOK_SECRET", "change-this")
PUBLIC_BASE_URL: Final = os.getenv("PUBLIC_BASE_URL")  # e.g. https://your-service.onrender.com
WEBHOOK_PATH: Final = f"/webhook/{WEBHOOK_SECRET}"

app = FastAPI()
ptb_app: Application | None = None

@app.on_event("startup")
async def on_startup():
    global ptb_app
    if not TOKEN or not PUBLIC_BASE_URL:
        raise RuntimeError("BOT_TOKEN and PUBLIC_BASE_URL must be set")
    ptb_app = (
        Application.builder()
        .token(TOKEN)
        .updater(None)  # FastAPI handles HTTP; no polling
        .build()
    )

    # Handlers
    from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello")

    def handle_response(text: str) -> str:
        return "this is a test response"

    async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(handle_response(update.message.text or ""))

    ptb_app.add_handler(CommandHandler("start", start))
    ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Set webhook
    url = PUBLIC_BASE_URL.rstrip("/") + WEBHOOK_PATH
    await ptb_app.bot.set_webhook(url=url, secret_token=WEBHOOK_SECRET)
    logger.info("Webhook set to %s", url)

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)
    await ptb_app.process_update(update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok"}
