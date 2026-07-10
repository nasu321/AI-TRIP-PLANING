"""
Report ORM model — stores generated PDF reports and delivery status.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

    pdf_filename = Column(String(300), nullable=True)
    pdf_path = Column(String(500), nullable=True)
    pdf_size_bytes = Column(Integer, nullable=True)

    whatsapp_sent = Column(Boolean, default=False)
    whatsapp_to = Column(String(30), nullable=True)
    whatsapp_message_sid = Column(String(100), nullable=True)
    whatsapp_sent_at = Column(DateTime, nullable=True)

    email_sent = Column(Boolean, default=False)
    email_to = Column(String(200), nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="reports")
