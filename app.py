from flask import Flask, request
import os, requests

app = Flask(__name__)
TOKEN = os.environ["BOT_TOKEN"]
TG = f"https://api.telegram.org/bot{TOKEN}"

@app.get("/")
def health(): return "ok"

@app.post("/webhook")
def webhook():
    update = request.get_json(silent=True) or {}
    msg = update.get("message") or {}
    text = (msg.get("text") or "").strip()
    if text.split()[0].split("@")[0] == "/start":
        requests.post(f"{TG}/sendMessage", data={
            "chat_id": str(msg["chat"]["id"]),
            "text": "hello!"
        })
    return "ok"
