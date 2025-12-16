#Simple script to test routing decision logic - whether to reply or escalate

from models import EmailEvent
from router.decision import handle_incoming_email
from datetime import datetime

def test_simple_reply_flow():
    ev = EmailEvent(
        id='t1',
        from_address='alice@example.com',
        to_address='support@example.com',
        subject='Question about product',
        body_text='Hello, how do I change my password?',
        timestamp=datetime.utcnow(),
        raw={}
    )
    res = handle_incoming_email(ev)
    assert res.reply_text != '' or res.should_escalate
