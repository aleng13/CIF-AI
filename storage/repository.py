from .db import SessionLocal
from .models import Conversation, Message, Escalation, AnalyticsEvent

def get_or_create_conversation(external_id=None):
    db = SessionLocal()
    conv = None
    if external_id:
        conv = db.query(Conversation).filter(Conversation.external_id==external_id).first()
    if not conv:
        conv = Conversation(external_id=external_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
    db.close()
    return conv

def save_message(conversation_id, sender, subject, body, metadata=None):
    db = SessionLocal()
    msg = Message(conversation_id=conversation_id, sender=sender, subject=subject, body=body, metadata=metadata or {})
    db.add(msg)
    db.commit()
    db.refresh(msg)
    db.close()
    return msg

def save_escalation(conversation_id, department, reason):
    db = SessionLocal()
    esc = Escalation(conversation_id=conversation_id, department=department, reason=reason)
    db.add(esc)
    db.commit()
    db.refresh(esc)
    db.close()
    return esc

def log_event(event_type, payload):
    db = SessionLocal()
    ev = AnalyticsEvent(event_type=event_type, payload=payload)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    db.close()
    return ev
