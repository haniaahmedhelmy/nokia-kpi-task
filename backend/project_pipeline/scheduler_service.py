from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from pathlib import Path
import json
import pytz

from project_pipeline.email_service import send_email_report

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = BASE_DIR / "settings.json"
scheduler = BackgroundScheduler(timezone="Africa/Cairo")

scheduler.start()

def read_settings():
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def schedule_email_job(sender_email: str, sender_password: str):
    settings = read_settings()

    freq = settings.get("frequency", "daily")
    time_str = settings.get("time", "12:00") or "12:00"
    days = settings.get("days", [])

    hour, minute = map(int, time_str.split(":"))

    scheduler.remove_all_jobs()

    if freq == "daily":
        trigger = CronTrigger(hour=hour, minute=minute)
    elif freq == "weekly":
        if not days:
            raise ValueError("Weekly schedule requires 'days'")
        trigger = CronTrigger(day_of_week=days[0], hour=hour, minute=minute)
    elif freq == "monthly":
        if not days:
            raise ValueError("Monthly schedule requires 'days'")
        trigger = CronTrigger(day=int(days[0]), hour=hour, minute=minute)
    else:
        raise ValueError(f"Unsupported frequency: {freq}")

    def job_wrapper():
        print(f"Job fired at {datetime.now()} (local Cairo time)")
        send_email_report()

    scheduler.add_job(
        func=job_wrapper,
        trigger=trigger,
        id="scheduled_email",
        replace_existing=True,
    )

    print(f"Scheduled email job: {freq} at {time_str}, days={days} (Cairo time)")
