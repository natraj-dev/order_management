from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.db.base_class import Base
from datetime import datetime


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True)

    discount_type = Column(String(20))
    discount_value = Column(Float)

    is_active = Column(Boolean, default=True)

    expiry_date = Column(DateTime, nullable=True)
    usage_limit = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
