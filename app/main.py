from fastapi import Request
from fastapi import FastAPI, Request
from app.db.base import Base
from app.db.session import engine

# routers
from app.routers.auth import router as auth_router
from app.routers.product import router as product_router
from app.routers.order import router as order_router
from app.routers.payment import router as payment_router
from app.routers.cart import router as cart_router
from app.routers.coupon import router as coupon_router
from app.routers.stock import router as stock_router
from app.core.logger import logger
import time
from app.routers import webhook


app = FastAPI()

# ✅ include routers (clean)
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(cart_router)
app.include_router(coupon_router)
app.include_router(stock_router)
app.include_router(webhook.router)

# thank-fine-amity-pride  clears-posh-honest-nice

# ✅ create tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API is running"}


# ✅ MODULE 15: ADVANCED LOGGING MIDDLEWARE


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # ✅ Request log (structured but same meaning)
    logger.info(
        f"REQUEST | method={request.method} path={request.url.path}"
    )

    try:
        response = await call_next(request)

        process_time = round((time.time() - start_time) * 1000, 2)

        # ✅ Response log
        logger.info(
            f"RESPONSE | status={response.status_code} time={process_time}ms path={request.url.path}"
        )

        return response

    except Exception as e:
        process_time = round((time.time() - start_time) * 1000, 2)

        # ✅ Error log (important for module)
        logger.error(
            f"ERROR | method={request.method} path={request.url.path} error={str(e)} time={process_time}ms"
        )

        raise e
