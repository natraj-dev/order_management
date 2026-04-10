from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.stock_log import StockLog

router = APIRouter(prefix="/stock", tags=["Stock Logs"])


@router.get("/logs")
def get_stock_logs(db: Session = Depends(get_db)):
    return db.query(StockLog).all()
