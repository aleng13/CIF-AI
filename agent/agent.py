from .groq_client import analyze, generate_reply
from models import AgentResult

AI_SIGNATURE = "\n\n—\nWritten by AI"

def analyze_for_routing(email_event, rag_docs):
    analysis = analyze(email_event.body_text, rag_docs)

    return AgentResult(
        reply_text="",
        summary=analysis.get("summary", ""),
        department=analysis.get("department"),
        should_escalate=analysis.get("escalate", True),
        confidence=analysis.get("confidence", 0.0),
        llm_metadata=analysis
    )

def generate_ai_reply(email_event, rag_docs):
    out = generate_reply(email_event.body_text, rag_docs)

    reply_text = out.get("reply_text", "") + AI_SIGNATURE

    return AgentResult(
        reply_text=reply_text,
        summary=out.get("summary", ""),
        department=None,
        should_escalate=False,
        confidence=1.0,
        llm_metadata={"model": "groq"}
    )
