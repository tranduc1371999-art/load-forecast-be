import asyncio
import json
import math
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/realtime", tags=["Realtime"])

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

FORECAST_FILE = DATA_DIR / "forecast_15min.csv"


def safe_float(value):
    try:
        value = float(value)
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    except Exception:
        return None


def load_forecast_data(date: Optional[str] = None):
    if not FORECAST_FILE.exists():
        raise FileNotFoundError(f"File not found: {FORECAST_FILE}")

    df = pd.read_csv(FORECAST_FILE)

    if "Timestamp" not in df.columns:
        raise ValueError("forecast_15min.csv must contain Timestamp column")

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp")

    if date:
        selected_date = pd.to_datetime(date).date()
        df = df[df["Timestamp"].dt.date == selected_date]

    return df


async def stream_forecast_points(
    date: Optional[str],
    interval: float,
    limit: Optional[int]
):
    try:
        df = load_forecast_data(date)

        if df.empty:
            payload = {
                "type": "error",
                "message": f"No data found for date: {date}"
            }
            yield f"event: error\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
            return

        count = 0

        for _, row in df.iterrows():
            payload = {
                "type": "load_point",
                "timestamp": row["Timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                "actual_load": safe_float(row.get("actual_load")),
                "forecast_load": safe_float(row.get("forecast_load")),
                "error": safe_float(row.get("error")),
                "error_percent": safe_float(row.get("error_percent")),
            }

            yield f"event: load_point\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

            count += 1

            if limit is not None and count >= limit:
                break

            await asyncio.sleep(interval)

        done_payload = {
            "type": "done",
            "message": "Realtime simulation completed",
            "total_points": count
        }

        yield f"event: done\ndata: {json.dumps(done_payload, ensure_ascii=False)}\n\n"

    except Exception as e:
        payload = {
            "type": "error",
            "message": str(e)
        }
        yield f"event: error\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.get("/stream")
def realtime_stream(
    date: Optional[str] = Query(default=None, description="Example: 2024-06-21"),
    interval: float = Query(default=2.0, description="Seconds between each point"),
    limit: Optional[int] = Query(default=None, description="Limit number of points")
):
    return StreamingResponse(
        stream_forecast_points(date=date, interval=interval, limit=limit),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/dates")
def get_available_dates():
    df = load_forecast_data()
    dates = sorted(df["Timestamp"].dt.strftime("%Y-%m-%d").unique().tolist())

    return {
        "success": True,
        "data": dates
    }