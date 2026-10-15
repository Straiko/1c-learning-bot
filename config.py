import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Also check parent directory if .env not in current folder
if not os.getenv("BOT_TOKEN"):
    load_dotenv(BASE_DIR.parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
