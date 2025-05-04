import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    DB_USER = os.getenv("DB_USER") or "user"
    DB_PASSWORD = os.getenv("DB_PASSWORD") or "password"

    DB_HOST = os.getenv("DB_HOST") or "db"
    DB_PORT = int(os.getenv("DB_PORT") or 3306)
    DB_NAME = os.getenv("DB_NAME") or "jdatabase"

    NOTIFIER_URL = os.getenv("NOTIFIER_URL") or "http://notifier:8500/notify"
    FRONTEND_URL = os.getenv("FRONTEND_URL") or "http://frontend:5500/notify"

print("🔧 Loaded DB Config:")
print(f"  Host: {Config.DB_HOST}")
print(f"  Port: {Config.DB_PORT}")
print(f"  User: {Config.DB_USER}")

print(f"  Name: {Config.DB_NAME}")
print(f"  Notifier URL: {Config.NOTIFIER_URL}")
