from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from pathlib import Path
import json
import pytz

from project_pipeline.email_service import send_email_report

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = BASE_DIR / "settings.json"

# Scheduler (runs in background with Cairo timezone)
scheduler = BackgroundScheduler(timezone="Africa/Cairo")
scheduler.start()

def read_settings():
    """Read settings.json config file."""
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def schedule_email_job():
    """Schedule email job based on settings.json."""
    settings = read_settings()
    freq = settings.get("frequency", "daily")   # daily / weekly / monthly
    time_str = settings.get("time", "12:00") or "12:00"
    days = settings.get("days", [])
    hour, minute = map(int, time_str.split(":"))

    # Clear old jobs before adding new one
    scheduler.remove_all_jobs()
    
    # Create trigger depending on frequency
    if freq == "daily":
        trigger = CronTrigger(hour=hour, minute=minute)

    elif freq == "weekly":
        if not days:
            raise ValueError("Weekly schedule requires 'days'")
        day = str(days[0]).capitalize()[:3]  # e.g. "Mon", "Tue"
        trigger = CronTrigger(day_of_week=day.lower(), hour=hour, minute=minute)    

    elif freq == "monthly":
        if not days:
            raise ValueError("Monthly schedule requires 'days'")
        day = int(days[0])  # must be numeric (e.g. 1–31)
        trigger = CronTrigger(day=day, hour=hour, minute=minute)    

    else:
        raise ValueError(f"Unsupported frequency: {freq}")

    
    def job_wrapper():
        print(f"Job fired at {datetime.now()} (local Cairo time)")
        send_email_report()

    # Add scheduled job
    scheduler.add_job(
        func=job_wrapper,
        trigger=trigger,
        id="scheduled_email",
        replace_existing=True,
    )

    print(f"Scheduled email job: {freq} at {time_str}, days={days} (Cairo time)")
