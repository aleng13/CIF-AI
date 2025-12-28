from storage import repository
from rag.search import search as rag_search
from agent.agent import analyze_for_routing, generate_ai_reply
from router.classifier import choose_department
from router.escalation import escalate
from EMail.gmail_client import GmailClient
from models import AgentResult

client = GmailClient()

DEPARTMENT_EMAILS = {
    "billing": "u2203002@rajagiri.edu.in",
    "technical": "u2203002@rajagiri.edu.in",
    "logistics": "u2203002@rajagiri.edu.in",
    "operations": "u2203002@rajagiri.edu.in",
    "sales": "u2203002@rajagiri.edu.in",
    "support": "u2203002@rajagiri.edu.in"
}

AI_SIGNATURE = "\n\n—\nWritten by AI"

def handle_incoming_email(email_event):
    # 1. Conversation
    conv = repository.get_or_create_conversation(
        external_id=email_event.from_address
    )
    conv_id = conv.id

    repository.save_message(
        conv_id,
        sender=email_event.from_address,
        subject=email_event.subject,
        body=email_event.body_text,
        mdata={"raw": email_event.raw}
    )

    # 2. RAG
    rag_docs = rag_search(email_event.body_text)

    # 3. LLM analysis
    analysis = analyze_for_routing(email_event, rag_docs)

    repository.log_event(
        "analysis_done",
        {"email_id": email_event.id, "analysis": analysis.llm_metadata}
    )

    # 4. HARD escalation rules (code-enforced)
    should_escalate = (
        analysis.should_escalate or analysis.confidence < 0.6
    )

    if should_escalate:
        dept = choose_department(analysis, email_event)
        reason = analysis.summary or "Escalated by AI"

        # ---- Customer-facing reply (hardcoded) ----
        customer_reply = (
            f"Hello,\n\n"
            f"Thank you for reaching out. "
            f"Your issue requires further review and has been escalated to our "
            f"{dept.capitalize()} team.\n\n"
            f"A team member will get back to you shortly."
            f"{AI_SIGNATURE}"
        )

        client.send_reply(
            to_email=email_event.from_address,
            subject="Re: " + (email_event.subject or ""),
            body_text=customer_reply
        )

        repository.save_message(
            conv_id,
            sender="AI",
            subject="Re: " + (email_event.subject or ""),
            body=customer_reply,
            mdata={"escalation": True, "department": dept}
        )

        # ---- Notify department ----
        dept_email = DEPARTMENT_EMAILS.get(dept, DEPARTMENT_EMAILS["support"])

        client.send_reply(
            to_email=dept_email,
            subject=f"[Escalation] New issue from {email_event.from_address}",
            body_text=(
                f"Conversation ID: {conv_id}\n"
                f"Customer: {email_event.from_address}\n\n"
                f"Summary:\n{analysis.summary}"
            )
        )

        # ---- Create escalation record ----
        esc = escalate(conv_id, dept, reason, context=rag_docs)

        repository.log_event(
            "escalation_created",
            {"escalation_id": esc.id, "department": dept}
        )

        return analysis

    # 5. Normal AI reply
    reply = generate_ai_reply(email_event, rag_docs)

    repository.save_message(
        conv_id,
        sender="AI",
        subject="Re: " + (email_event.subject or ""),
        body=reply.reply_text,
        mdata={"summary": reply.summary}
    )

    repository.log_event(
        "reply_sent",
        {"email_id": email_event.id, "preview": reply.reply_text[:120]}
    )

    client.send_reply(
        to_email=email_event.from_address,
        subject="Re: " + (email_event.subject or ""),
        body_text=reply.reply_text
    )

    return reply
