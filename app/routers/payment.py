from app.services.payment_service import confirm_payment
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.payment import PaymentCreate
from app.services.payment_service import create_payment, process_payment, create_payment_intent
from app.core.security import get_current_user
from app.db.session import get_db
from pydantic import BaseModel


router = APIRouter(prefix="/payment", tags=["Payments"])


class PaymentRequest(BaseModel):
    amount: int


@router.post("/create-intent")
def create_intent(data: PaymentRequest):
    return create_payment_intent(data.amount)


class ConfirmRequest(BaseModel):
    payment_intent_id: str
    order_id: int


@router.post("/confirm")
def confirm(data: ConfirmRequest, db: Session = Depends(get_db)):
    return confirm_payment(data.payment_intent_id, data.order_id,
                           db)

# ✅ CREATE PAYMENT


@router.post("/")
def make_payment(
    data: PaymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return create_payment(
        db,
        data.order_id,
        data.payment_method,
        background_tasks
    )


# ✅ PROCESS PAYMENT (simulate success/failure)
@router.post("/pay")
def pay(
    order_id: int,
    amount: float,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return process_payment(
        db,
        order_id,
        amount,
        background_tasks   # ✅ FIXED
    )


# ✅ RETRY PAYMENT
@router.post("/retry")
def retry_payment(
    payment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    from app.models.payment import Payment

    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status.lower() == "success":
        return {"message": "Already paid"}

    # ✅ retry payment with background task
    new_payment = process_payment(
        db,
        payment.order_id,
        payment.amount,
        background_tasks   # ✅ FIXED
    )

    return {
        "message": "Retry attempted",
        "new_status": new_payment.status,
        "transaction_id": new_payment.transaction_id
    }
