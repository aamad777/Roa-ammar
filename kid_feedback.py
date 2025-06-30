
import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

def send_email_to_dad(child_name, question, answer):
    sender = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASS")
    receiver = os.getenv("DAD_EMAIL")

    try:
        msg = MIMEMultipart()
        msg["Subject"] = f"{child_name} needs help!"
        msg["From"] = sender
        msg["To"] = receiver

        body = f"""{child_name} didn't understand this question:

❓ {question}

💬 Suggested Answer:
{answer}
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender, password)
            smtp.sendmail(sender, receiver, msg.as_string())

        return True, "✅ Email was sent successfully."
    except Exception as e:
        return False, f"❌ Email failed: {e}"
