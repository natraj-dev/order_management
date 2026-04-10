
from fastapi import APIRouter, Request, HTTPException, Depends
import stripe
from app.db.session import SessionLocal
from app.models.order import Order
from app.models.payment import Payment, PaymentStatus

router = APIRouter(prefix="/webhook", tags=["Webhook"])

endpoint_secret = "whsec_8e6bb64b33e0c7aa453060d79a465d027efab53e705890a42fb38eda6ba34214"


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        db = SessionLocal()

        # ✅ PAYMENT SUCCESS
        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]

            stripe_id = intent["id"]
            amount = intent["amount"] / 100

            # 🔥 update payment
            payment = db.query(Payment).filter(
                Payment.transaction_id == stripe_id
            ).first()

            if payment:
                payment.status = PaymentStatus.SUCCESS

                # 🔥 update order
                order = db.query(Order).filter(
                    Order.id == payment.order_id
                ).first()

                if order:
                    order.status = "PAID"
                    db.commit()

            print(f"✅ Payment success updated DB: {stripe_id}")

        # ❌ PAYMENT FAILED
        elif event["type"] == "payment_intent.payment_failed":
            intent = event["data"]["object"]
            stripe_id = intent["id"]

            payment = db.query(Payment).filter(
                Payment.transaction_id == stripe_id
            ).first()

            if payment:
                payment.status = PaymentStatus.FAILED

            db.commit()

            print(f"❌ Payment failed: {stripe_id}")

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
