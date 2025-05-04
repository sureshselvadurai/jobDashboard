import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    DB_USER = os.getenv("DB_USER", "user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_PORT = int(os.getenv("DB_PORT") or 3306)  # Safely fallback to 3306 if empty
    DB_NAME = os.getenv("DB_NAME", "jdatabase")

    NOTIFIER_URL = os.getenv("NOTIFIER_URL", "http://notifier:8500/notify")

# Optional: print summary for debug (mask sensitive values)
print("🔧 Loaded DB Config:")
print(f"  Host: {Config.DB_HOST}")
print(f"  Port: {Config.DB_PORT}")
print(f"  User: {Config.DB_USER}")
print(f"  Name: {Config.DB_NAME}")
print(f"  Notifier URL: {Config.NOTIFIER_URL}")
