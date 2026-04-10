from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


# ✅ Better enum (clean & reusable)
class PaymentStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"))

    amount = Column(Float, nullable=False)

    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    payment_method = Column(String(50), nullable=True)

    transaction_id = Column(String(255), unique=True, nullable=True)

    retry_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ Relationship
    order = relationship("Order", back_populates="payments")
