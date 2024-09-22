from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import API_URL, PROD_TELEGRAM_BOT_TOKEN

USER_API_URL = API_URL + "/api/users"
# Temporarily store user session data with their tokens
user_sessions = {}

keyboard = [
    [InlineKeyboardButton("Open WebApp", web_app=WebAppInfo(url=f"{USER_API_URL}/"))],
    [InlineKeyboardButton("Your info", callback_data='user_info')],
    [InlineKeyboardButton("Logout", callback_data='logout')],
]
reply_markup = InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_uid = str(update.effective_user.id)

    try:
        # Check if the user already exists in the database
        username = update.effective_user.username
        response = requests.get(f"{USER_API_URL}/info/{telegram_uid}")
        if not response.json():
            # if no use then create
            response = requests.post(f"{USER_API_URL}/create", json={"nickname": username, "telegram_uid": telegram_uid})
            if response.status_code != 200:
                await update.message.reply_text("Failed to create user.")
                return

        # Using requests to make a POST request to login the user
        response = requests.post(f"{USER_API_URL}/login", params={"telegram_uid": telegram_uid})
        if response.status_code == 200:
            token_data = response.json()
            # Save the token for further requests
            user_sessions[telegram_uid] = token_data['access_token']

            await update.message.reply_text("Login successful! Choose an option:", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Login failed. Please try again.")
    except Exception as e:
        await update.message.reply_text(f"Error during login: {str(e)}")

# Callback query handler for stats, create user, and logout
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_uid = str(query.from_user.id)
    token = user_sessions.get(telegram_uid)

    if not token:
        await query.edit_message_text("You are not logged in.")
        return

    headers = {"Authorization": f"Bearer {token}"}


    if query.data == "user_info":
        try:
            response = requests.get(f"{USER_API_URL}/info/{telegram_uid}", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                user_info = f"Nickname: {user_data['nickname']}\nCoins: {user_data['coins']}\nRating: {user_data['rating']}"
                await query.edit_message_text(user_info)
                await query.edit_message_reply_markup(reply_markup=reply_markup)
        except Exception as e:
            await query.edit_message_text(f"Failed to get user info: {str(e)}")


    elif query.data == 'logout':
        # Logout request using requests
        try:
            response = requests.post(f"{USER_API_URL}/logout", params={"telegram_uid": telegram_uid})
            if response.status_code == 200:
                user_sessions.pop(telegram_uid, None)
                await query.edit_message_text("You have been logged out.")
            else:
                await query.edit_message_text("Failed to log out.")
        except Exception as e:
            await query.edit_message_text(f"Logout failed: {str(e)}")

# Main function to run the bot
def main():
    # Initialize the application with the bot token
    application = ApplicationBuilder().token(PROD_TELEGRAM_BOT_TOKEN).build()

    # Add command handler for /start
    application.add_handler(CommandHandler("start", start))

    # Add callback query handler for inline button actions
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
