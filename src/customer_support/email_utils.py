"""
Refer the Google_Config.md file for instructions on how to set up Gmail SMTP.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email: str, subject: str, body: str) -> None:
    gmail_address = os.getenv("GMAIL_ADDRESS")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_address or not gmail_app_password:
        raise ValueError("GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set in .env")

    msg = MIMEMultipart()
    msg["From"] = gmail_address
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_address, gmail_app_password)
        server.send_message(msg)


if __name__ == "__main__":
    # Quick manual test
    from dotenv import load_dotenv
    load_dotenv()
    send_email(
        to_email="your_mail@gmail.com", #To test the email sending, replace this with your email address
        subject="Test email from Customer Support Agent",
        body="If you're reading this, Gmail sending works.",
    )
    print("Email sent successfully")