from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import BackgroundTasks, HTTPException

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.models.stock_log import StockLog

from app.services.email_templates import order_confirmation_template, cancel_template
from app.services.background_tasks import (
    process_order_task,
    send_email_task
)

from app.core.logger import logger


# =========================
# CREATE ORDER
# =========================
def create_order(
    db: Session,
    user_id: int,
    items,
    background_tasks: BackgroundTasks
):
    total_amount = 0
    order_items = []

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        for item in items:
            product = (
                db.query(Product)
                .filter(Product.id == item.product_id)
                .with_for_update()
                .first()
            )

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

            total_amount += product.price * item.quantity

            order_items.append({
                "product": product,
                "quantity": item.quantity
            })

        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )

        db.add(order)
        db.flush()

        for item in order_items:
            product = item["product"]

            db_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item["quantity"],
                price=product.price
            )

            product.stock -= item["quantity"]

            # LOW STOCK ALERT
            if product.stock < 5:
                print(f"⚠️ Low stock: {product.name} ({product.stock})")

                background_tasks.add_task(
                    send_email_task,
                    "natarajanelangovan14@gmail.com",
                    "Low Stock Alert",
                    f"{product.name} low stock ({product.stock})"
                )

            log = StockLog(
                product_id=product.id,
                change=-item["quantity"],
                action="ORDER"
            )

            db.add(log)
            db.add(db_item)

        db.commit()
        db.refresh(order)

    except HTTPException as e:
        db.rollback()
        raise e

    except Exception as e:
        db.rollback()
        logger.error(f"🔥 ORDER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Order creation failed")

    # BACKGROUND TASKS
    background_tasks.add_task(process_order_task, order.id)

    message = order_confirmation_template(order.id)

    background_tasks.add_task(
        send_email_task,
        user.email,
        "Order Confirmation",
        message
    )

    return order


# =========================
# CANCEL ORDER
# =========================
def cancel_order(
    db: Session,
    order_id: int,
    user_id: int,
    background_tasks: BackgroundTasks
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(User).filter(User.id == user_id).first()

    order.status = OrderStatus.CANCELLED
    db.commit()

    message = cancel_template(order.id)

    background_tasks.add_task(
        send_email_task,
        user.email,
        "Order Cancelled",
        message
    )

    return order


# =========================
# ADMIN DASHBOARD
# =========================
def get_total_orders(db: Session):
    return db.query(Order).count()


def get_total_revenue(db: Session):
    revenue = db.query(func.sum(Order.total_amount)).scalar()
    return revenue or 0


def get_top_products(db: Session):
    results = (
        db.query(
            Product.name,
            func.sum(OrderItem.quantity).label("total_sold")
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .group_by(Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    return [{"product": r[0], "sold": r[1]} for r in results]


def get_user_stats(db: Session):
    total_users = db.query(User).count()

    active_users = db.query(Order.user_id).distinct().count()

    return {
        "total_users": total_users,
        "active_users": active_users
    }
