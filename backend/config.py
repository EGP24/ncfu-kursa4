import os

from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/shoplist_app')
JWT_SECRET = os.getenv('JWT_SECRET', 'super-secret-key')
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8080'))

