from models import EmailEvent
from datetime import datetime

def parse_message_to_event(msg):
    return EmailEvent(
        id=msg.get('id'),
        from_address=msg.get('from'),
        to_address=msg.get('to'),
        subject=msg.get('subject'),
        body_text=msg.get('body'),
        timestamp=datetime.fromisoformat(msg.get('timestamp')),
        raw=msg
    )
