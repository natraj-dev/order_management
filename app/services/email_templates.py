def order_confirmation_template(order_id: int):
    return f"""
    <html>
    <body style="font-family: Arial;">

        <h2 style="color: green;">Order Confirmed 🎉</h2>

        <p>Your order <b>#{order_id}</b> has been placed successfully.</p>

        <p>We are preparing your items for shipment.</p>

        <hr>

        <p style="color: gray;">Thank you for shopping with us ❤️</p>

    </body>
    </html>
    """


def payment_template(order_id: int, status: str):
    return f"""
    <html>
    <body style="font-family: Arial;">

        <h2 style="color: blue;">Payment Update 💳</h2>

        <p>Your payment for order <b>#{order_id}</b> is:</p>

        <h3 style="color: {'green' if status == 'SUCCESS' else 'red'};">
            {status}
        </h3>

        <hr>

        <p>Thank you for your purchase!</p>

    </body>
    </html>
    """


def cancel_template(order_id: int):
    return f"""
    <html>
    <body>

        <h2 style="color: red;">Order Cancelled ❌</h2>

        <p>Your order <b>#{order_id}</b> has been cancelled.</p>

    </body>
    </html>
    """
