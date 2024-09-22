from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, \
    MessageHandler, filters
import requests
import os
import sys
from telegram.error import BadRequest


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scheme import UserUpdate
from logger import create_logger
from config import API_URL, ADMIN_TELEGRAM_BOT_TOKEN

ADMIN_API_URL = API_URL + "/api/admin"

ASK_FOR_NICKNAME, ASK_FOR_UID, START_UPDATE, CHOOSE_FIELD, ENTER_COINS, ENTER_RATING, CONFIRM_CHANGES = range(7)

TOKEN = ""


admin_bot_logger = create_logger("../logs/app.log", "admin_bot")

keyboard = [
    [InlineKeyboardButton("Open WebApp", web_app=WebAppInfo(url=f"{ADMIN_API_URL}/"))],
    [InlineKeyboardButton("Get user info", callback_data='user_info')],
    [InlineKeyboardButton("Get all users", callback_data='all_users')],
    [InlineKeyboardButton("Get statistics", callback_data='stats')],
    [InlineKeyboardButton("Get UID by nickname", callback_data='user_by_nickname')],
    [InlineKeyboardButton("Update user", callback_data='update_user')],
]
reply_markup = InlineKeyboardMarkup(keyboard)

field_keyboard = [
    [InlineKeyboardButton("Update Coins", callback_data='update_coins')],
    [InlineKeyboardButton("Update Rating", callback_data='update_rating')],
    [InlineKeyboardButton("Confirm Changes", callback_data='confirm_changes')],
    [InlineKeyboardButton("Cancel", callback_data='cancel')],
]
field_markup = InlineKeyboardMarkup(field_keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TOKEN
    response = requests.post(f"{API_URL}/api/users/login", params={"telegram_uid": update.effective_user.id})
    if response.status_code != 200:
        await update.message.reply_text("You are not logged in.")
        return
    TOKEN = response.json()['access_token']
    await update.message.reply_text("Welcome to the admin bot! Choose an option:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query


    match query.data:
        case 'user_info':
            await query.edit_message_text("Enter UID:")
            return ASK_FOR_UID
        case 'all_users':
            await handle_all_users(query)
            admin_bot_logger.info(f"User{query.from_user.username} requested all users.")
        case 'stats':
            await handle_stats(query)
            admin_bot_logger.info(f"User{query.from_user.username} requested stats.")
        case 'user_by_nickname':
            await query.edit_message_text("Enter Nickname:")
            return ASK_FOR_NICKNAME
        case 'update_user':
            await query.edit_message_text("Enter the UID of the user you want to update:")
            return START_UPDATE


"""User info"""
async def handle_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TOKEN
    try:
        telegram_uid = update.message.text
        await update.message.reply_text(f"Fetching user info for UID: {telegram_uid}...")
        response = requests.get(f"{ADMIN_API_URL}/get_user_by_uid/{telegram_uid}", headers={
            "Authorization": f"Bearer {TOKEN}"
        })
        if response.status_code == 200:
            user = response.json()
            message = f"User info:\n" \
                      f"Nickname: {user['nickname']}\n" \
                      f"Rating: {user['rating']}\n" \
                      f"Coins: {user['coins']}\n" \
                      f"Last login: {user['last_login']}"
            await update.message.reply_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text("Failed to get user info.")
    except BadRequest as e:
        admin_bot_logger.error(f"Failed to get user info: {e}")

    return ConversationHandler.END

"""All Users"""
async def handle_all_users(query):
    global TOKEN
    try:
        response = requests.get(f"{ADMIN_API_URL}/get_users", headers={
            "Authorization": f"Bearer {TOKEN}"
        })
        if response.status_code == 200:
            users = response.json()
            message = "All users:\n"
            for user in users:
                message += f"Nickname: {user['nickname']}\n" \
                           f"Rating: {user['rating']}\n" \
                           f"Coins: {user['coins']}\n" \
                           f"Last login: {user['last_login']}\n\n"
            await query.edit_message_text(message)
            await query.edit_message_reply_markup(reply_markup)
        else:
            await query.edit_message_text("Failed to get all users.")
    except BadRequest as e:
        admin_bot_logger.error(f"Failed to get all users: {e}")

"""Stats"""
async def handle_stats(query):
    global TOKEN
    try:
        response = requests.get(f"{ADMIN_API_URL}/stats", headers={
            "Authorization": f"Bearer {TOKEN}"
        })
        if response.status_code == 200:
            stats = response.json()
            message = f"Total users: {stats['total_users']}\n" \
                      f"Online users: {stats['online_users']}\n" \
                      f"High rating users: {stats['high_rating_users_count']}"
            await query.edit_message_text(message)
            await query.edit_message_reply_markup(reply_markup)
        else:
            await query.edit_message_text("Failed to get stats.")

    except BadRequest as e:
        admin_bot_logger.error(f"Failed to get stats: {e}")

"""Get user by nickname"""
async def handle_user_by_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TOKEN
    try:
        username = update.message.text
        response = requests.get(f"{ADMIN_API_URL}/get_user_by_nickname/{username}", headers={
            "Authorization": f"Bearer {TOKEN}"
        })
        if response.status_code == 200:
            user = response.json()
            message = f"Nickname: {user['nickname']}\n" \
                      f"UID: {user['telegram_uid']}\n"
            await update.message.reply_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text("Failed to get user by nickname.")
    except BadRequest as e:
        admin_bot_logger.error(f"Failed to get user by nickname: {e}")
    return ConversationHandler.END


"""Update user"""
async def start_update_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text
    context.user_data['uid'] = uid  # Store UID in user data
    await update.message.reply_text("Choose the field you want to update:", reply_markup=field_markup)
    return CHOOSE_FIELD

# Handler for choosing which field to update
async def choose_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'update_coins':
        await query.edit_message_text("Enter the new number of coins:")
        return ENTER_COINS
    elif query.data == 'update_rating':
        await query.edit_message_text("Enter the new rating:")
        return ENTER_RATING
    elif query.data == 'confirm_changes':
        await confirm_changes(update, context)
        return CONFIRM_CHANGES
    elif query.data == 'cancel':
        await query.edit_message_text("Update canceled.")
        return ConversationHandler.END

# Handler to collect coins input
async def enter_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        coins = int(update.message.text)
        context.user_data['coins'] = coins
        await update.message.reply_text("Coins updated. Choose another action or confirm changes:", reply_markup=field_markup)
        return CHOOSE_FIELD
    except ValueError:
        await update.message.reply_text("Please enter a valid number for coins.")
        return ENTER_COINS

# Handler to collect rating input
async def enter_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rating = int(update.message.text)
        context.user_data['rating'] = rating
        await update.message.reply_text("Rating updated. Choose another action or confirm changes:", reply_markup=field_markup)
        return CHOOSE_FIELD
    except ValueError:
        await update.message.reply_text("Please enter a valid number for rating.")
        return ENTER_RATING

# Handler to confirm changes and send the update request
async def confirm_changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TOKEN
    uid = context.user_data['uid']
    changes = {
        'coins': context.user_data.get('coins'),
        'rating': context.user_data.get('rating')
    }

    # Filter out None values
    changes = {k: v for k, v in changes.items() if v is not None}

    user = UserUpdate(
        coins=changes['coins'],
        rating=changes['rating']
    )
    query = update.callback_query
    # Send the update request to the backend
    try:
        response = requests.put(f"{ADMIN_API_URL}/update_user/{uid}", data=user, headers={
            "Authorization": "Bearer " + TOKEN,
        })
        if response.status_code == 200:
            await query.edit_message_text("User updated successfully.", reply_markup=reply_markup)
        else:
            await query.edit_message_text("Failed to update user.", reply_markup=reply_markup)
    except BadRequest as e:
        admin_bot_logger.error(f"Failed to update user: {e}")
        await query.edit_message_text("An error occurred while updating the user.", reply_markup=reply_markup)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


"""Main"""
def main():
    # Initialize the application with the bot token
    application = ApplicationBuilder().token(ADMIN_TELEGRAM_BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback)],
        states={
            ASK_FOR_UID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_info)],
            ASK_FOR_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_by_nickname)],
            START_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_update_user)],
            CHOOSE_FIELD: [CallbackQueryHandler(choose_field)],
            ENTER_COINS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_coins)],
            ENTER_RATING: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_rating)],
            CONFIRM_CHANGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_changes)],

        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    # Add command handler for /start
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    # Add callback query handler for inline button actions
    application.add_handler(CallbackQueryHandler(handle_callback))

    admin_bot_logger.info("Starting admin bot...")
    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
