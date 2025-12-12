"""Mocked Groq client. Returns structured JSON as if from an LLM."""
import random

def analyze(email_text, context_docs):
    # simple heuristics for demo
    text = email_text.lower()
    confidence = 0.95 if 'refund' in text or 'not arrived' in text or 'cancel' in text else 0.85
    sentiment = 'negative' if 'not' in text or 'refund' in text else 'neutral'
    department = 'billing' if 'refund' in text or 'invoice' in text else ('logistics' if 'shipping' in text or 'arrived' in text else 'technical')
    escalate = True if confidence < 0.9 or 'refund' in text else False
    summary = (text[:140] + '...') if len(text) > 140 else text
    return {
        'intent': 'customer_query',
        'confidence': confidence,
        'sentiment': sentiment,
        'department': department,
        'escalate': escalate,
        'summary': summary,
        'suggested_action': 'escalate' if escalate else 'reply'
    }

def generate_reply(email_text, context_docs):
    # return a polite canned reply using context docs if possible
    if 'refund' in email_text.lower():
        reply = """Hi — sorry to hear about this. I have started a refund process for your order and forwarded this to Billing. You will receive an update within 5–7 business days."""
    else:
        reply = """Hi — thanks for reaching out. We are looking into this and will get back to you shortly."""
    summary = reply[:200]
    return {'reply_text': reply, 'summary': summary}
