from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.order import Order


def create_payment(db: Session, order_id: int, method: str):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise Exception("Order not found")

    # simulate success
    status = "Success"

    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        status=status,
        payment_method=method
    )

    # update order status
    order.status = "Confirmed"

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment
