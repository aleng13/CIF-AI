# Customer-AI — Phase 1 Template

Minimal, local-first template for the email → routing → RAG → Groq-agent pipeline.
All external integrations are mocked so you can run it locally.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# initialize db and run the poller (mocked)
python main.py
```

This template:
- Polls a mocked Gmail inbox (local JSON) every 10 seconds
- Runs routing decision (mock LLM analysis)
- Stores messages and escalations in SQLite
- Prints AI replies or escalation actions

Files of interest:
- `main.py` — entrypoint
- `email/poller.py` — polling loop (mock)
- `router/decision.py` — main coordinator
- `agent/groq_client.py` — mocked LLM responses
- `storage/` — SQLite models and simple repo

