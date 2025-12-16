"""Entrypoint for local Phase-1 demo. Initializes DB and starts poller."""
from storage.db import init_db
from storage.models import Base
from EMail.poller import start_polling
import os

def main():
    os.makedirs('data', exist_ok=True)
    init_db(Base)
    print('Starting email poller (press Ctrl+C to stop)...')
    start_polling()

if __name__ == '__main__':
    main()
