from dotenv import load_dotenv
import os

load_dotenv('.env')

PROD_TELEGRAM_BOT_TOKEN = os.getenv('PROD_TELEGRAM_BOT_TOKEN')
TOKEN_EXPIRATION = int(os.getenv('TOKEN_EXPIRATION'))
TOKEN_SECRET = os.getenv('TOKEN_SECRET')
TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM')
API_URL = str(os.getenv('API_URL'))

ADMIN_TELEGRAM_BOT_TOKEN = os.getenv("ADMIN_TELEGRAM_BOT_TOKEN")