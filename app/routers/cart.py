from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.db.session import get_db
from app.schemas.cart import AddToCart
from app.services.cart_service import add_to_cart
from app.core.security import get_current_user
from app.services.cart_service import (
    add_to_cart, checkout_cart, get_cart_summary, update_cart_item, remove_cart_item)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/")
def view_cart(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    db_user = db.query(User).filter(User.email == user["sub"]).first()
    return get_cart_summary(db, db_user.id)


@router.post("/add")
def add_item(
    data: AddToCart,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_user = db.query(User).filter(User.email == user["sub"]).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return add_to_cart(
        db,
        db_user.id,
        data.product_id,
        data.quantity
    )


@router.put("/update")
def update_cart(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_user = db.query(User).filter(User.email == user["sub"]).first()

    return update_cart_item(db, db_user.id, product_id, quantity)


@router.delete("/remove/{product_id}")
def remove_item(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_user = db.query(User).filter(User.email == user["sub"]).first()

    return remove_cart_item(db, db_user.id, product_id)


@router.post("/checkout")
def checkout(
    coupon_code: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_user = db.query(User).filter(User.email == user["sub"]).first()

    return checkout_cart(db, db_user.id, coupon_code)
