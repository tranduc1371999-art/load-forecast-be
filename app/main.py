from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Load Forecast API",
    description="API for electric load forecast dashboard",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local dev cho phép tất cả
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Load Forecast API is running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "UP"
    }


@app.get("/api/forecast/chart")
def get_forecast_chart():
    return {
        "region": "mien_bac",
        "date": "2026-06-14",
        "data": [
            {
                "time": "00:00",
                "actual_load": 12000,
                "forecast_load": 11850
            },
            {
                "time": "01:00",
                "actual_load": 11600,
                "forecast_load": 11520
            },
            {
                "time": "02:00",
                "actual_load": 11200,
                "forecast_load": 11350
            }
        ]
    }