from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


# ✅ Enum (clean)
class PaymentStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    # ✅ FK (allow NULL initially if not linked yet)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)

    # ✅ Amount
    amount = Column(Float, nullable=False)

    # ✅ Store as string internally (important fix)
    status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )

    # ✅ Stripe uses "card"
    payment_method = Column(String(50), nullable=True)

    # ✅ Stripe PaymentIntent ID (pi_xxx)
    transaction_id = Column(String(255), unique=True, nullable=False)

    # ✅ Retry tracking
    retry_count = Column(Integer, default=0)

    # ✅ Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ Relationship (correct)
    order = relationship("Order", back_populates="payments")
