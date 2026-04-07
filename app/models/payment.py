from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime
from app.db.base import Base
from datetime import datetime


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    amount = Column(Float)
    status = Column(String(50))
    payment_method = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
