from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText
from app.core.config import settings


def send_email(to: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
            server.send_message(msg)

        print("Email sent successfully")

    except Exception as e:
        print("Email failed:", str(e))


def send_order_email(background_tasks: BackgroundTasks, email: str):
    background_tasks.add_task(
        send_email,
        email,
        "Order Confirmation",
        "Your order has been placed successfully!"
    )


def send_payment_email(background_tasks: BackgroundTasks, email: str):
    background_tasks.add_task(
        send_email,
        email,
        "Payment Success",
        "Your payment was successful!"
    )
