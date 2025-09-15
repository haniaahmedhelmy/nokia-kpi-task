import json
import smtplib
import ssl
from pathlib import Path
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = BASE_DIR / "settings.json"
PPT_PATH = BASE_DIR / "report.pptx"

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

def send_email_report():
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        settings = json.load(f)

    recipients = settings.get("mailing_list", "").split(";")
    recipients = [r.strip() for r in recipients if r.strip()]

    if not recipients:
        raise ValueError("No recipients in settings.json mailing_list")

    if not PPT_PATH.exists():
        raise FileNotFoundError(f"PowerPoint not found at {PPT_PATH}")

    msg = EmailMessage()
    msg["Subject"] = "Nokia KPIs Report"
    msg["From"] = SMTP_FROM
    msg["To"] = ", ".join(recipients)
    msg.set_content("Attached is the latest KPI report in PowerPoint format.")

    with open(PPT_PATH, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=PPT_PATH.name,
        )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"Report sent to {recipients}")
