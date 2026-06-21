from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.forecast_api import router as forecast_router
from app.realtime_api import router as realtime_router

app = FastAPI(title="Load Forecast API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://anhvhn.duckdns.org:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forecast_router)
app.include_router(realtime_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "UP"
    }