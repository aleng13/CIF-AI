KEYWORD_MAP = {
    'refund': 'billing',
    'payment': 'billing',
    'invoice': 'billing',
    'shipping': 'logistics',
    'delivery': 'logistics',
    'not working': 'technical',
    'error': 'technical',
    'cancel': 'operations'
}

def choose_department(analysis, email_event=None):
    # prefer LLM suggestion
    dept = None
    if analysis and getattr(analysis, 'department', None):
        dept = analysis.department
    # fallback keyword map
    text = (email_event.body_text if email_event else '').lower()
    for k,v in KEYWORD_MAP.items():
        if k in text:
            return v
    return dept or 'support'
