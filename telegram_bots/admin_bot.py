from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import API_URL

ADMIN_API_URL = API_URL + "/admin"

keyboard = [
    [InlineKeyboardButton("Open WebApp", web_app=WebAppInfo(url=f"{ADMIN_API_URL}/"))],
    [InlineKeyboardButton("Get user info", callback_data='user_info')],
    [InlineKeyboardButton("Get all users", callback_data='all_users')],
    [InlineKeyboardButton("Get amount of users", callback_data='amount_users')],
    [InlineKeyboardButton("Get amount of online users", callback_data='amount_online_users')],
    [InlineKeyboardButton("Get users by coins and rating", callback_data='users_by_coins_rating')],
    [InlineKeyboardButton("Get UID by nickname", callback_data='user_by_nickname')],
    [InlineKeyboardButton("Update user", callback_data='update_user')],
]
reply_markup = InlineKeyboardMarkup(keyboard)


