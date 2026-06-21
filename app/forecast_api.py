import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fastapi import APIRouter

router = APIRouter(prefix="/api/forecast", tags=["Forecast"])

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DATA_DIR = Path(
    os.getenv("FORECAST_DATA_DIR")
    or os.getenv("DATA_DIR")
    or BASE_DIR / "data"
)

def dataframe_to_records(df: pd.DataFrame):
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    df = df.astype(object).where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def read_csv_as_json(file_name: str):
    file_path = DATA_DIR / file_name

    if not file_path.exists():
        return {
            "success": False,
            "message": f"File not found: {file_name}",
            "file_path": str(file_path),
            "data": []
        }

    df = pd.read_csv(file_path)

    return {
        "success": True,
        "file_name": file_name,
        "total": len(df),
        "data": dataframe_to_records(df)
    }


@router.get("/short-term/15min")
def get_short_term_15min_forecast():
    return read_csv_as_json("forecast_short_term_15min.csv")


@router.get("/short-term/hourly")
def get_short_term_hourly_forecast():
    return read_csv_as_json("forecast_short_term_hourly.csv")


@router.get("/medium-term/daily")
def get_medium_term_daily_forecast():
    return read_csv_as_json("forecast_medium_term_daily.csv")


@router.get("/medium-term/monthly")
def get_medium_term_monthly_forecast():
    return read_csv_as_json("forecast_medium_term_monthly.csv")


@router.get("/long-term/monthly")
def get_long_term_monthly_forecast():
    return read_csv_as_json("forecast_long_term_monthly.csv")


@router.get("/long-term/scenarios")
def get_long_term_scenarios_forecast():
    return read_csv_as_json("forecast_long_term_scenarios.csv")


@router.get("/metrics")
def get_model_metrics():
    file_path = DATA_DIR / "model_metrics.json"

    if not file_path.exists():
        return {
            "success": False,
            "message": "model_metrics.json not found",
            "file_path": str(file_path)
        }

    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    payload["success"] = True
    return payload
