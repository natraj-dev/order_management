from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import create_payment
from app.core.security import get_current_user
from fastapi import BackgroundTasks
from app.services.email_service import send_payment_email
from app.models.user import User
from app.models.order import Order

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse)
def make_payment(
    data: PaymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        payment = create_payment(db, data.order_id, data.payment_method)

        order = db.query(Order).filter(Order.id == data.order_id).first()
        db_user = db.query(User).filter(User.id == order.user_id).first()

        send_payment_email(background_tasks, db_user.email)

        return payment

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
