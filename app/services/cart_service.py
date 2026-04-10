from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.coupon import Coupon
from datetime import datetime


# ✅ Get or create cart
def get_or_create_cart(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


# ✅ Add to cart
def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int):
    cart = get_or_create_cart(db, user_id)

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid quantity")

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    # 🔥 CASE 1: NEW ITEM
    if not item:
        if product.stock < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Only {product.stock} available"
            )

        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(item)

    # 🔥 CASE 2: EXISTING ITEM
    else:
        new_total = item.quantity + quantity

        if product.stock < new_total:
            raise HTTPException(
                status_code=400,
                detail=f"Only {product.stock} available"
            )

        item.quantity = new_total

    db.commit()
    db.refresh(item)

    return item


# ✅ View cart
def get_cart_summary(db: Session, user_id: int):
    cart = get_or_create_cart(db, user_id)

    items_data = []
    total = 0

    for item in cart.items:
        product = db.query(Product).filter(
            Product.id == item.product_id).first()

        if not product:
            continue

        # 🔥 ADD THIS WARNING
        if product.stock == 0:
            status = "OUT OF STOCK"
        elif product.stock < item.quantity:
            status = f"Only {product.stock} left"
        else:
            status = "Available"

        item_total = product.price * item.quantity
        total += item_total

        items_data.append({
            "product": product.name,
            "quantity": item.quantity,
            "price": product.price,
            "total": item_total,
            "status": status   # ✅ NEW FIELD
        })

    return {
        "items": items_data,
        "total": total
    }


# ✅ Checkout (FINAL CLEAN VERSION)
def checkout_cart(db: Session, user_id: int, coupon_code: str = None):

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    subtotal = 0

    try:
        # 🔒 STOCK VALIDATION WITH LOCK
        products_map = {}

        for item in cart.items:
            product = db.query(Product).filter(
                Product.id == item.product_id
            ).with_for_update().first()

            if not product:
                raise HTTPException(
                    status_code=404, detail="Product not found")

            if product.stock == 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"{product.name} is out of stock"
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Only {product.stock} available for {product.name}"
                )

            subtotal += product.price * item.quantity
            products_map[item.product_id] = product   # store for reuse

        # ✅ TAX
        tax = subtotal * 0.05

        # ✅ DISCOUNT
        discount = 0

        if coupon_code:
            coupon = db.query(Coupon).filter(
                Coupon.code == coupon_code,
                Coupon.is_active == True
            ).first()

            if not coupon:
                raise HTTPException(status_code=400, detail="Invalid coupon")

            # ✅ expiry check
            if coupon.expiry_date and coupon.expiry_date < datetime.utcnow():
                raise HTTPException(status_code=400, detail="Coupon expired")

            # ✅ usage limit check
            if coupon.used_count >= coupon.usage_limit:
                raise HTTPException(
                    status_code=400, detail="Coupon usage limit reached")

            if coupon.discount_type == "percentage":
                discount = subtotal * (coupon.discount_value / 100)

            elif coupon.discount_type == "flat":
                discount = coupon.discount_value

        total_amount = max(subtotal + tax - discount, 0)

        # ✅ CREATE ORDER
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )

        db.add(order)
        db.flush()

        # ✅ CREATE ITEMS + REDUCE STOCK
        for item in cart.items:
            product = products_map[item.product_id]

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=product.price
            )

            product.stock -= item.quantity
            db.add(order_item)

        # ✅ CLEAR CART
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

        db.commit()

    except HTTPException as e:
        db.rollback()
        raise e

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "subtotal": subtotal,
        "tax": tax,
        "discount": discount,
        "total": total_amount
    }


# ✅ Update cart
def update_cart_item(db: Session, user_id: int, product_id: int, quantity: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid quantity")

    item.quantity = quantity
    db.commit()

    return {"message": "Cart updated"}


# ✅ Remove item
def remove_cart_item(db: Session, user_id: int, product_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    return {"message": "Item removed"}
