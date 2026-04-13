"""Payment Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="VND")
    method = Column(String(50), nullable=False)  # stripe, paypal, momo, vnpay, cod, bank_transfer
    status = Column(String(30), default="pending")  # pending, processing, completed, failed, refunded, cancelled

    # External references
    payment_intent_id = Column(String(200), nullable=True)
    transaction_id = Column(String(200), nullable=True)
    gateway_response = Column(JSON, nullable=True)

    # Refund
    refunded_amount = Column(Float, default=0.0)
    refund_reason = Column(Text, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    # Metadata
    description = Column(String(500), nullable=True)
    payment_metadata = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="payment")
