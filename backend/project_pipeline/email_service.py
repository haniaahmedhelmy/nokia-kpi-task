import json
import smtplib
import ssl
from pathlib import Path
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define project paths
BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = BASE_DIR / "settings.json"   
PPT_PATH = BASE_DIR / "report.pptx"       

# Email server configuration (from .env )
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

def send_email_report():
    # Load recipients from settings.json
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        settings = json.load(f)

    recipients = settings.get("mailing_list", "").split(";")
    recipients = [r.strip() for r in recipients if r.strip()]  # Clean up emails

    if not recipients:
        raise ValueError("No recipients in settings.json mailing_list")

    # Check if report file exists
    if not PPT_PATH.exists():
        raise FileNotFoundError(f"PowerPoint not found at {PPT_PATH}")

    # Build email message
    msg = EmailMessage()
    msg["Subject"] = "Nokia KPIs Report"
    msg["From"] = SMTP_FROM
    msg["To"] = ", ".join(recipients)
    msg.set_content("Attached is the latest KPI report in PowerPoint format.")

    # Attach PowerPoint file
    with open(PPT_PATH, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=PPT_PATH.name,
        )

    # Send email securely using SSL
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"Report sent to {recipients}")
