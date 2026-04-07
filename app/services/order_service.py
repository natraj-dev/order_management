from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.services.email_templates import order_confirmation_template
from app.services.email_service import send_email


def create_order(db: Session, user_id: int, items):
    total_amount = 0
    order_items = []

    for item in items:
        product = db.query(Product).filter(
            Product.id == item.product_id).first()

        if not product:
            raise Exception("Product not found")

        if product.stock < item.quantity:
            raise Exception("Not enough stock")

        total_amount += product.price * item.quantity

        order_items.append({
            "product": product,
            "quantity": item.quantity
        })

    order = Order(user_id=user_id, total_amount=total_amount)
    db.add(order)
    db.commit()
    db.refresh(order)

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

    return order
