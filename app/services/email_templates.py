def order_confirmation_template(order_id: int):
    return f"""
      Order Confirmed!

    Your order #{order_id} has been placed successfully.

    Thank you for shopping with us!
    """


def payment_success_template(order_id: int):
    return f"""
      Payment Successful!

    Your payment for order #{order_id} was successful.

    Your order is now being processed.
    """


def payment_failed_template(order_id: int):
    return f"""
      Payment Failed!

    Your payment for order #{order_id} failed.

    Please try again.
    """


def order_status_template(order_id: int, status: str):
    return f"""
      Order Update

    Your order #{order_id} status is now: {status}

    Thank you!
    """
