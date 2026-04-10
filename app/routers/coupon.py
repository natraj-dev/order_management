from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.models.coupon import Coupon

router = APIRouter(prefix="/coupon", tags=["Coupon"])


@router.post("/create")
def create_coupon(
    code: str,
    discount_type: str,
    discount_value: float,
    expiry_date: str = None,
    usage_limit: int = 1,
    db: Session = Depends(get_db)
):
    existing = db.query(Coupon).filter(Coupon.code == code).first()
    if existing:
        return {"error": "Coupon already exists"}

    coupon = Coupon(
        code=code,
        discount_type=discount_type,
        discount_value=discount_value,
        expiry_date=datetime.fromisoformat(
            expiry_date) if expiry_date else None,
        usage_limit=usage_limit
    )
    db.add(coupon)
    db.commit()
    return {"message": "Coupon created"}
