from app.models.payment import PaymentStatus
from app.models.payment import Payment, PaymentStatus
from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, HTTPException

from app.models.payment import Payment
from app.models.order import Order
from app.models.user import User

from app.services.email_templates import payment_template
from app.services.background_tasks import send_email_task

from app.core.logger import logger

import random
import uuid
import time

import stripe
from app.core.stripe_config import stripe


def create_payment_intent(amount: int):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount * 100,
            currency='inr',
            payment_method_types=["card"],
        )

        return {
            "client_secret": payment_intent.client_secret,
            "id": payment_intent.id
        }

    except Exception as e:
        return {"stripe error", str(e)}

        return {
            "error": str(e)
        }


def confirm_payment(payment_intent_id: str, order_id: int, db: Session):
    try:
        # 🔹 Confirm Stripe payment
        payment = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method="pm_card_visa"
        )

        # 🔹 Convert status
        if payment.status == "succeeded":
            status_enum = PaymentStatus.SUCCESS
        elif payment.status == "failed":
            status_enum = PaymentStatus.FAILED
        else:
            status_enum = PaymentStatus.PENDING

        # 🔹 Save payment
        save_payment(
            db=db,
            order_id=order_id,
            amount=payment.amount / 100,
            status=payment.status,
            transaction_id=payment.id
        )

        # ✅ 🔥 UPDATE ORDER STATUS HERE
        if payment.status == "succeeded":
            order = db.query(Order).filter(Order.id == order_id).first()

            if order:
                order.status = "PAID"   # ✅ THIS LINE
                db.commit()             # ✅ SAVE CHANGE

        return {
            "status": payment.status,
            "id": payment.id
        }

    except Exception as e:
        return {"error": str(e)}


def save_payment(db, order_id, amount, status, transaction_id):

    # ✅ Convert Stripe status → Enum
    if status == "succeeded":
        status_enum = PaymentStatus.SUCCESS
    elif status == "failed":
        status_enum = PaymentStatus.FAILED
    else:
        status_enum = PaymentStatus.PENDING

    payment = Payment(
        order_id=order_id,
        amount=amount,
        status=status_enum,
        payment_method="card",
        transaction_id=transaction_id
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment
# =========================
# CREATE PAYMENT
# =========================


def create_payment(
    db: Session,
    order_id: int,
    method: str,
    background_tasks: BackgroundTasks
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    user = db.query(User).filter(User.id == order.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # ✅ Simulate delay
        print("⏳ Processing payment...")
        time.sleep(2)

        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            status="SUCCESS",
            payment_method=method,
            transaction_id=str(uuid.uuid4()),
            retry_count=0
        )

        order.status = "CONFIRMED"

        db.add(payment)
        db.commit()
        db.refresh(payment)

        # ✅ FIXED LOGGER
        logger.info(f"💰 Payment SUCCESS for order {order.id}")

    except Exception as e:
        db.rollback()
        logger.error(f"🔥 PAYMENT ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment failed")

    # ✅ EMAIL
    message = payment_template(order.id, "SUCCESS")

    background_tasks.add_task(
        send_email_task,
        user.email,
        "Payment Successful",
        message
    )

    return payment


# =========================
# PROCESS PAYMENT (RETRY LOGIC)
# =========================
def process_payment(
    db: Session,
    order_id: int,
    amount: float,
    background_tasks: BackgroundTasks
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    user = db.query(User).filter(User.id == order.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    retry_count = 0
    max_retries = 2

    while retry_count <= max_retries:
        try:
            print(f"🔁 Retry {retry_count}")

            time.sleep(2)

            success = random.choice([True, False])

            if success:
                status = "SUCCESS"
                order.status = "CONFIRMED"
            else:
                status = "FAILED"

            payment = Payment(
                order_id=order.id,
                amount=amount,
                status=status,
                payment_method="CARD",
                transaction_id=str(uuid.uuid4()),
                retry_count=retry_count
            )

            db.add(payment)
            db.commit()
            db.refresh(payment)

            # ✅ FIXED LOGGER
            logger.info(f"💰 Payment {status} for order {order.id}")

            # ✅ EMAIL
            message = payment_template(order.id, status)

            background_tasks.add_task(
                send_email_task,
                user.email,
                "Payment Update",
                message
            )

            if status == "SUCCESS":
                return payment

            retry_count += 1

        except Exception as e:
            db.rollback()
            logger.error(f"🔥 PAYMENT ERROR: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Payment processing failed"
            )

    raise HTTPException(status_code=400, detail="Payment failed after retries")
