from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.base import Base
from datetime import datetime


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  # ✅ add index for search
    description = Column(String(500))
    price = Column(Float, index=True)       # ✅ useful for filtering
    stock = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
