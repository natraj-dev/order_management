from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText
from app.core.config import settings


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


def send_email(to_email: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.EMAIL, settings.EMAIL_PASSWORD)

        server.sendmail(settings.EMAIL, to_email, msg.as_string())
        server.quit()

        print(f"✅ Email sent to {to_email}")

    except Exception as e:
        print("❌ Email failed:", str(e))


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
