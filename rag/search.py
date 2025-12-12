"""Simple RAG mock: returns sample docs from data/sample_docs.json based on basic keyword match."""
import json, os

DATA_PATH = os.path.join('data', 'sample_docs.json')

def ensure_sample_docs():
    if not os.path.exists('data'):
        os.makedirs('data', exist_ok=True)
    if not os.path.exists(DATA_PATH):
        sample = [
            {'id': 'doc1', 'text': 'Refund policy: refunds are issued within 5-7 business days.', 'source': 'policy'},
            {'id': 'doc2', 'text': 'Shipping times: standard shipping 10-14 days, express 2-4 days.', 'source': 'shipping'},
            {'id': 'doc3', 'text': 'Password reset steps: go to account settings -> reset password.', 'source': 'help'},
        ]
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(sample, f, indent=2)

def search(query, top_k=2):
    ensure_sample_docs()
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        docs = json.load(f)
    # very naive: return docs that contain any keyword from query lowercased
    q = query.lower()
    scored = []
    for d in docs:
        score = 0
        for token in q.split():
            if token in d['text'].lower():
                score += 1
        if score > 0:
            scored.append((score, d))
    scored.sort(reverse=True, key=lambda x: x[0])
    if not scored:
        # fallback: return first top_k docs
        return docs[:top_k]
    return [d for _, d in scored[:top_k]]
