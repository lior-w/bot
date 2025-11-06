from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = '8448271704:AAE0E3jAM2OC0jbP9RNLy6bKQq3J7UQTRLI'
BOT_USERNAME: Final = '@TikTokUrl2025Bot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text('Hello')
	
	
def handle_response(text: str) -> str:
	return 'this is a test response'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
	message_type: str = update.message.chat.type
	text: str = update.message.text
	
	print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
	
	response: str = handle_response(text)
	
	print('Bot:', response)
	await update.message.reply_text(response)
	
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
	print(f'Update {update} casued error {context.error}')
	
if __name__ == '__main__':
	print('Starting bot...')
	app = Application.builder().token(TOKEN).build()
	
	app.app_handler(CommandHandler('start', start_command))
	
	app.add_handler(MessageHandler(filters.TEXT, handle_message))
	
	app.add_error_handler(error)
	
	print('Polling...')
	app.run_polling(poll_interval=3)
