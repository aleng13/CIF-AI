from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    external_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    sender = Column(String)
    subject = Column(String)
    body = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON)

class Escalation(Base):
    __tablename__ = "escalations"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    department = Column(String)
    reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id = Column(Integer, primary_key=True)
    event_type = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
