import time
from config import POLL_INTERVAL
from .gmail_client import MockGmailClient
from .parser import parse_message_to_event
from router.decision import handle_incoming_email

client = MockGmailClient()

def start_polling():
    try:
        while True:
            unread = client.list_unread_messages()
            if unread:
                print(f'Found {len(unread)} unread message(s).')
            for m in unread:
                print(f'Processing message {m["id"]} subject: {m.get("subject")}')
                event = parse_message_to_event(m)
                handle_incoming_email(event)
                client.mark_as_read(m['id'])
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print('Poller stopped.')
