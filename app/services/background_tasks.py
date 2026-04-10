import time
from app.services.email_service import send_email

# ✅ Email simulation


def send_email_task(email: str, subject: str, message: str):
    print(f"📧 Sending email to {email}...")
    send_email(email, subject, message)
    time.sleep(2)
    print(f"✅ Email sent: {subject}")


# ✅ Order processing
def process_order_task(order_id: int):
    print(f"📦 Processing order {order_id}...")
    time.sleep(2)
    print(f"✅ Order {order_id} processed")


# ✅ Payment log
def payment_log_task(order_id: int, status: str):
    print(f"💳 Logging payment for Order {order_id}...")
    time.sleep(1)
    print(f"✅ Payment {status} logged")
