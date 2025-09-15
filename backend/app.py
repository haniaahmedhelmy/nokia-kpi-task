from fastapi import FastAPI, Depends, HTTPException
from pathlib import Path
from typing import List, Literal, Union, Optional
from pydantic import BaseModel
from contextlib import asynccontextmanager
import json
import os

from auth_service import (
    app as auth_service_app,
    auth_startup,
    auth_shutdown,
    UserOut,
    current_user,
)
from fastapi.middleware.cors import CORSMiddleware
from data_cleaner import clean_and_aggregate
from project_pipeline.excel_export import generate_excel_report
from project_pipeline.ppt_export import export_to_ppt
from project_pipeline.scheduler_service import schedule_email_job


BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = Path(__file__).parent / "settings.json"


class ChartSetting(BaseModel):
    type: Literal["list", "equation"]
    value: Union[List[str], str]


ALL_KPIS = [f"kpi{i:03d}" for i in range(1, 10)]


class Settings(BaseModel):
    days_back: int = 7
    frequency: Literal["daily", "weekly", "monthly"] = "daily"
    time: Optional[str] = ""
    days: List[Union[str, int]] = []
    mailing_list: str = ""
    line_chart: ChartSetting = ChartSetting(type="list", value=ALL_KPIS)
    bar_chart: ChartSetting = ChartSetting(type="list", value=ALL_KPIS)


def read_settings() -> Settings:
    if not SETTINGS_PATH.exists():
        s = Settings()
        SETTINGS_PATH.write_text(s.model_dump_json(indent=2))
        return s

    data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    s = Settings(**data)

    if not s.line_chart.value:
        s.line_chart.value = ALL_KPIS
    if not s.bar_chart.value:
        s.bar_chart.value = ALL_KPIS

    return s


def write_settings(s: Settings) -> None:
    SETTINGS_PATH.write_text(s.model_dump_json(indent=2))


@asynccontextmanager
async def lifespan(app: FastAPI):
    input_file = BASE_DIR / "dataset.csv"
    output_file = BASE_DIR / "backend" / "cleaned_dataset.csv"
    clean_and_aggregate(input_file, output_file)
    print(f"Cleaned dataset saved to {output_file}")
    generate_excel_report()
    await auth_startup()
    yield
    await auth_shutdown()


app = FastAPI(lifespan=lifespan, title="Main Backend", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/settings", response_model=Settings)
def get_settings():
    return read_settings()


@app.put("/settings", response_model=Settings)
def put_settings(s: Settings, user: UserOut = Depends(current_user)):
    write_settings(s)
    generate_excel_report()
    sender_email = user.email
    sender_password = os.getenv("SMTP_PASS")
    schedule_email_job(sender_email, sender_password)
    return s


app.mount("/auth", auth_service_app)


@app.post("/export-ppt")
def export_ppt():
    path = export_to_ppt()
    return {"ppt_path": str(path)}


@app.post("/schedule-email")
async def schedule_email(user: UserOut = Depends(current_user)):
    try:
        sender_email = user.email
        sender_password = os.getenv("SMTP_PASS")
        schedule_email_job(sender_email, sender_password)
        return {"message": "Email scheduled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
