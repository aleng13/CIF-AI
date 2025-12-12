from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class EmailEvent(BaseModel):
    id: str
    from_address: str
    to_address: str
    subject: Optional[str]
    body_text: str
    timestamp: datetime
    raw: Dict = {}

class AgentResult(BaseModel):
    reply_text: str
    summary: str
    department: Optional[str]
    should_escalate: bool
    confidence: float
    llm_metadata: Dict = {}
