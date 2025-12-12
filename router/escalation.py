from storage.repository import save_escalation
def escalate(conversation_id, department, reason, context=None):
    record = save_escalation(conversation_id, department, reason)
    # Phase-1 behavior: print escalation; later integrate with ticketing/email
    print('=== ESCALATION CREATED ===')
    print(f'conversation_id={conversation_id} department={department} reason={reason}')
    return record
