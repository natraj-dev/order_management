from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from datetime import datetime
from app.db.base import Base


class StockLog(Base):
    __tablename__ = "stock_logs"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    change = Column(Integer)  # + or -
    action = Column(String(50))  # ORDER / RESTOCK
    created_at = Column(DateTime, default=datetime.utcnow)
