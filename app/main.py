from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.routers.auth import router as auth_router
from app.routers.product import router as product_router
from app.routers.order import router as order_router
from app.routers.payment import router as payment_router


# import models
from app.models import user, product, order, payment

app = FastAPI()

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(payment_router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API is running"}
