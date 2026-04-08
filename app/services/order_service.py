from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, HTTPException

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User

from app.services.email_service import send_email
from app.services.email_templates import order_confirmation_template


def create_order(
    db: Session,
    user_id: int,
    items,
    background_tasks: BackgroundTasks
):
    total_amount = 0
    order_items = []

    # ✅ Get user email
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Process items
    for item in items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

        total_amount += product.price * item.quantity

        order_items.append({
            "product": product,
            "quantity": item.quantity
        })

    # ✅ Create order
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status="PENDING"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # ✅ Create order items + reduce stock
    for item in order_items:
        db_item = OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            price=item["product"].price
        )

        item["product"].stock -= item["quantity"]

        db.add(db_item)

    db.commit()

    # ✅ SEND EMAIL (BACKGROUND TASK)
    background_tasks.add_task(
        send_email,
        user.email,
        "Order Confirmation",
        order_confirmation_template(order.id)
    )

    return order
