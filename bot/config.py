import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "8076309526:AAGQueK-PFsJJYLdAl7g0cFggWdqvC3TFIc")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/progress.db")
DEBUG = os.getenv("DEBUG", "False") == "True"

