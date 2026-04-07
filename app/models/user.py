from sqlalchemy import Column, Integer, String, Enum
from app.db.base import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    customer = "customer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.customer)
