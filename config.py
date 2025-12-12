from dotenv import load_dotenv
import os
load_dotenv()

MODE = os.environ.get("MODE", "LOCAL")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 10))
SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", "./data/customer_ai.db")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "mock")
