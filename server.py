import os
import re
import requests
import logging
from typing import Final
from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)

# ---- Config ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("tg-bot")

TOKEN: Final = os.getenv("BOT_TOKEN")
PUBLIC_BASE_URL: Final = os.getenv("PUBLIC_BASE_URL")  # e.g. https://yourapp.onrender.com
WEBHOOK_SECRET: Final = os.getenv("WEBHOOK_SECRET", "change-me")  # must match set_webhook
WEBHOOK_PATH: Final = f"/webhook/{WEBHOOK_SECRET}"

app = FastAPI()
ptb_app: Application | None = None


# ---- Handlers ----
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello")

def get_redirected_url(url: str):
    r = requests.get(url, allow_redirects=True)
    return r.url
    
def clean_tiktok_url(url: str) -> str:
    if '&' in url:
        return url.split('&', 1)[0]
    return url
    
def process_tiktok_url(url: str) -> str:
    redirected_url = get_redirected_url(url)
    clean_url = clean_tiktok_url(redirected_url)
    return clean_url
    
def extract_tiktok_shortlink(text: str) -> str | None:
    pattern = r"https://vt\.tiktok\.com/[A-Za-z0-9]+/"
    match = re.search(pattern, text)
    return match.group(0) if match else None

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if url := extract_tiktok_shortlink(text):
        await update.message.reply_text(process_tiktok_url(url))
    else:
        await update.message.reply_text("no valid link found")


# ---- Lifecycle ----
@app.on_event("startup")
async def on_startup():
    global ptb_app
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")
    if not PUBLIC_BASE_URL:
        raise RuntimeError("PUBLIC_BASE_URL is missing")
    if not WEBHOOK_SECRET or WEBHOOK_SECRET == "change-me":
        raise RuntimeError("WEBHOOK_SECRET is missing or default")

    # Build PTB app without Updater (ASGI handles HTTP)
    ptb_app = Application.builder().token(TOKEN).updater(None).build()

    # Add handlers
    ptb_app.add_handler(CommandHandler("start", start_cmd))
    ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))

    # Initialize + start PTB
    await ptb_app.initialize()

    # Set webhook to exact URL (no redirects)
    webhook_url = PUBLIC_BASE_URL.rstrip("/") + WEBHOOK_PATH
    await ptb_app.bot.set_webhook(url=webhook_url, secret_token=WEBHOOK_SECRET)
    logger.info("Webhook set to %s", webhook_url)

    # Start app (jobs, persistence hooks, etc.)
    await ptb_app.start()
    logger.info("PTB Application started")

@app.on_event("shutdown")
async def on_shutdown():
    if ptb_app is not None:
        await ptb_app.stop()
        await ptb_app.shutdown()
        logger.info("PTB Application stopped")

# ---- Routes ----
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    # Validate Telegram’s secret header
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)  # type: ignore[arg-type]
    await ptb_app.process_update(update)
    return {"ok": True}

@app.get("/")
async def health():
    return {"status": "ok"}
