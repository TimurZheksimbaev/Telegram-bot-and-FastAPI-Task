from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import requests
import os
from config import PROD_TELEGRAM_BOT_TOKEN, API_URL

# API URL from environment variable

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Open WebApp", web_app=WebAppInfo(url=f"{API_URL}/")),
            InlineKeyboardButton("Get Stats", callback_data='get_stats'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

# Callback handler for stats
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Fetch user stats from the API
    if query.data == 'get_stats':
        try:
            response = requests.get(f"{API_URL}/users")
            users = response.json()
            total_users = len(users)
            await query.edit_message_text(f"Total Users: {total_users}")
        except Exception as e:
            await query.edit_message_text(f"Failed to get stats: {str(e)}")

# Main function to run the bot
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram Bot Token
    application = ApplicationBuilder().token(PROD_TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
