from pydantic import BaseModel
from typing import List


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    payment_status: str | None

    class Config:
        from_attributes = True
