from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import create_order
from app.core.security import get_current_user
from app.models.user import User
from fastapi import BackgroundTasks
from app.services.email_service import send_order_email
from app.models.user import User
from app.core.security import require_admin
from app.models.order import Order
from app.models.order import OrderStatus
from app.core.security import get_current_user
from app.services.email_service import send_email
from app.services.email_templates import order_confirmation_template
from app.models.user import User
from app.models.payment import Payment

router = APIRouter(prefix="/orders", tags=["Orders"])


#  Create Order

@router.post("/", response_model=OrderResponse)
def create_new_order(
    data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        db_user = db.query(User).filter(User.email == user["sub"]).first()

        order = create_order(db, db_user.id, data.items)

        background_tasks.add_task(
            send_email,
            to=db_user.email,
            subject="Order Confirmation",
            body=order_confirmation_template(order.id)
        )

        send_order_email(background_tasks, db_user.email)

        return order

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# get order by id

@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    db.commit()

    return {"message": f"Order updated to {status}"}


# a customer can cancel the order

@router.put("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != db.query(User).filter(User.email == user["sub"]).first().id:
        raise HTTPException(status_code=403, detail="Not your order")

    if order.status == OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=400, detail="Cannot cancel delivered order")

    order.status = OrderStatus.CANCELLED
    db.commit()

    return {"message": "Order cancelled"}

# current customer can view the his own order


@router.get("/my-orders", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    db_user = db.query(User).filter(User.email == user["sub"]).first()

    orders = db.query(Order).filter(Order.user_id == db_user.id).all()

    return orders


# a Admin can view all the orders

@router.get("/admin/all-orders")
def get_all_orders(
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    orders = db.query(Order).all()

    result = []

    for order in orders:
        payment = db.query(Payment).filter(
            Payment.order_id == order.id).first()

        result.append({
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "status": order.status,  # order status
            "payment_status": payment.status if payment else "Pending"
        })

    return result
