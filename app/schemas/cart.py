from pydantic import BaseModel


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class AddToCart(BaseModel):
    product_id: int
    quantity: int


class CartResponse(BaseModel):
    product_id: int
    quantity: int

    class Config:
        orm_mode = True
