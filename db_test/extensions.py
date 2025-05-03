from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from cryptography.fernet import Fernet
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

bcrypt = Bcrypt()
jwt = JWTManager()
fernet = Fernet(os.getenv("FERNET_KEY"))


def encrypt(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()

def send_order_confirmation(to_email, order, line_items):
    from_email = os.getenv("GOOGLE_MAIL")
    password = os.getenv("GOOGLE_PASSWORD")

    subject = "Your Order Confirmation"
    item_lines = []
    total = 0
    for item in line_items.data:
        name = item.description
        quantity = item.quantity
        amount_each = item.price.unit_amount / 100  
        subtotal = amount_each * quantity
        total += subtotal
        item_lines.append(f"- {name} x{quantity} = {subtotal:.2f}kr")

    items_text = "\n".join(item_lines)

    body = f"""
    Hi there,

    Thank you for dining with us!

    Your order (ID: {order}) has been confirmed.

    Order Summary:
    {items_text}

    Total: ${total:.2f}
    
    Best regards,
    jamnaw
    """

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
        print("Confirmation email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")