from fastapi import BackgroundTasks
from app.utils.email import send_email


def send_welcome_email(background_tasks: BackgroundTasks, email: str):
    background_tasks.add_task(
        send_email,
        email,
        "Welcome!",
        "Thanks for registering."
    )
