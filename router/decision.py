from storage import repository
from rag.search import search as rag_search
from agent.agent import analyze_for_routing, generate_reply
from router.classifier import choose_department
from router.escalation import escalate
from models import AgentResult

def handle_incoming_email(email_event):
    # 1. get or create convo
    conv = repository.get_or_create_conversation(external_id=email_event.from_address)
    conv_id = conv.id
    repository.save_message(conv_id, sender=email_event.from_address, subject=email_event.subject, body=email_event.body_text, metadata={'raw': email_event.raw})
    # 2. RAG search
    rag_docs = rag_search(email_event.body_text)
    # 3. Initial analysis
    analysis = analyze_for_routing(email_event, rag_docs)
    repository.log_event('analysis_done', {'email_id': email_event.id, 'analysis': analysis.llm_metadata})
    # 4. Decide escalation
    if analysis.should_escalate:
        dept = choose_department(analysis, email_event)
        reason = analysis.summary or 'Escalation recommended by agent'
        esc = escalate(conv_id, dept, reason, context=rag_docs)
        repository.log_event('escalation_created', {'escalation_id': esc.id, 'department': dept})
        return analysis
    # 5. Generate reply
    reply = generate_reply(email_event, rag_docs)
    repository.save_message(conv_id, sender='AI', subject='Re: ' + (email_event.subject or ''), body=reply.reply_text, metadata={'summary': reply.summary})
    repository.log_event('reply_sent', {'email_id': email_event.id, 'reply_preview': reply.reply_text[:120]})
    print('=== AI Reply ===')
    print(reply.reply_text)
    return reply
