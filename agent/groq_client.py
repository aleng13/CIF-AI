# agent/groq_client.py

import os
import json
from groq import Groq
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"   

def _safe_json_parse(text: str) -> Dict:
    """
    Ensures the LLM output is valid JSON.
    If parsing fails, return a low-confidence fallback.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "sentiment": "unknown",
            "department": "support",
            "escalate": True,
            "summary": "LLM output could not be parsed",
            "suggested_action": "human_review"
        }

def analyze(email_text: str, context_docs: List[Dict]) -> Dict:
    """
    Analyze email for routing + escalation.
    """
    context_str = "\n".join(
        f"- {d.get('text', '')}" for d in context_docs
    )

    system_prompt = """
You are an AI customer-support triage assistant.

Your task:
1. Understand the user's issue
2. Decide if this should be handled by AI or escalated to a human
3. If escalation is needed, choose the correct department

Return ONLY valid JSON in this exact schema:

{
  "intent": "<short label>",
  "confidence": <float 0-1>,
  "sentiment": "positive|neutral|negative",
  "department": "billing|technical|logistics|sales|operations|support",
  "escalate": true|false,
  "summary": "<1-2 sentence internal summary>",
  "suggested_action": "<short instruction>"
}

Rules:
- Escalate if confidence < 0.6
- Escalate for refunds, billing disputes, cancellations, complaints
- Be conservative: when unsure, escalate
"""

    user_prompt = f"""
EMAIL:
{email_text}

CONTEXT DOCUMENTS:
{context_str}
"""

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=512,
    )

    raw = response.choices[0].message.content.strip()
    return _safe_json_parse(raw)


def generate_reply(email_text: str, context_docs: List[Dict]) -> Dict:
    """
    Generate customer-facing reply.
    """
    context_str = "\n".join(
        f"- {d.get('text', '')}" for d in context_docs
    )

    system_prompt = """
You are a professional customer support agent.

Write a clear, polite, and helpful email reply.
Rules:
- Do NOT promise refunds or actions unless stated
- Keep tone calm and professional
- Keep reply under 150 words
- No internal notes
"""

    user_prompt = f"""
CUSTOMER EMAIL:
{email_text}

REFERENCE INFO:
{context_str}
"""

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=400,
    )

    reply_text = response.choices[0].message.content.strip()

    return {
        "reply_text": reply_text,
        "summary": reply_text[:200]
    }
