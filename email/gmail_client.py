"""Mock Gmail client that reads from ./data/mock_emails.json (for local dev)."""
import json, os
from datetime import datetime

DATA_PATH = os.path.join('data', 'mock_emails.json')

class MockGmailClient:
    def __init__(self):
        # ensure file exists with a sample if missing
        if not os.path.exists('data'):
            os.makedirs('data', exist_ok=True)
        if not os.path.exists(DATA_PATH):
            sample = [{
                "id": "msg-1",
                "from": "user@example.com",
                "to": "support@example.com",
                "subject": "Order not received - refund request",
                "body": "Hi, I placed an order two weeks ago and it hasn't arrived. I want a refund.",
                "timestamp": datetime.utcnow().isoformat(),
                "read": False
            }]
            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(sample, f, indent=2)

    def list_unread_messages(self):
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            items = json.load(f)
        return [m for m in items if not m.get('read', False)]

    def get_message(self, msg_id):
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            items = json.load(f)
        for m in items:
            if m['id'] == msg_id:
                return m
        return None

    def mark_as_read(self, msg_id):
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            items = json.load(f)
        for m in items:
            if m['id'] == msg_id:
                m['read'] = True
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2)
