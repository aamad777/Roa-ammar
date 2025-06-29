
import streamlit as st
import smtplib
import os
from dotenv import load_dotenv
import random

load_dotenv()

def send_email_to_dad(child_name, question):
    sender = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASS")
    receiver = os.getenv("DAD_EMAIL")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender, password)
            subject = f"{child_name} needs help!"
            body = f"{child_name} didn't understand the question: '{question}'"
            message = f"Subject: {subject}\n\n{body}"
            smtp.sendmail(sender, receiver, message)
        return True, "✅ Email was sent successfully."
    except Exception as e:
        return False, f"❌ Email failed: {e}"

def render_kid_feedback_ui(child_name, question, answer):
    if not child_name or not question:
        return

    safe_key = f"{child_name}_{question}".replace(" ", "_").replace("?", "").replace("'", "").lower()
    yes_key = f"{safe_key}_yes"
    no_key = f"{safe_key}_no"

    col1, col2 = st.columns(2)

    if col1.button("👍 I understand it!", key=yes_key):
        a = random.randint(1, 3)
        b = random.randint(1, 3)
        st.session_state[f"{safe_key}_quiz"] = f"🍌 Fruit Quiz Time! What is {a} bananas + {b} bananas?"

    if col2.button("👎 I don't understand", key=no_key):
        sent, debug_msg = send_email_to_dad(child_name, question)
        st.session_state[f"{safe_key}_sent"] = sent
        st.session_state[f"{safe_key}_debug"] = debug_msg

    if f"{safe_key}_quiz" in st.session_state:
        st.info(st.session_state[f"{safe_key}_quiz"])

    if f"{safe_key}_sent" in st.session_state:
        if st.session_state[f"{safe_key}_sent"]:
            st.success("📧 Email sent to Dad!")
        else:
            st.error("⚠️ Failed to send email.")
        with st.expander("🔍 Debug Info"):
            st.code(st.session_state[f"{safe_key}_debug"])
