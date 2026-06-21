import json
from pathlib import Path

import pandas as pd
from fastapi import APIRouter

router = APIRouter(prefix="/api/forecast", tags=["Forecast"])

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


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


@router.get("/hourly")
def get_hourly_forecast():
    return read_csv_as_json("forecast_hourly.csv")


@router.get("/daily")
def get_daily_forecast():
    return read_csv_as_json("forecast_daily.csv")


@router.get("/monthly")
def get_monthly_forecast():
    return read_csv_as_json("forecast_monthly.csv")


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