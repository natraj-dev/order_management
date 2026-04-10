from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.cart import CartItemCreate
from app.services.cart_service import add_to_cart
from app.db.session import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/add")
def add_item_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return add_to_cart(
        db=db,
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity
    )
