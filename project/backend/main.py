import logging
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from .scheduler import refresh_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import gus, names

app = FastAPI(
    title="Trendy imion w Polsce API",
    description=(
        "API udostępniające dane o imionach nadawanych dzieciom w Polsce w 2024 roku "
        "z podziałem na powiaty i województwa. "
        "Dane pochodzą z dwóch źródeł: pliku CSV Ministerstwa Cyfryzacji (USC) "
        "oraz REST API Banku Danych Lokalnych GUS (BDL)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(names.router)
app.include_router(gus.router)

Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()

scheduler.add_job(
    refresh_data,
    trigger="cron",
    day=1,
    hour=3,
    minute=0
)

# scheduler.add_job(
#     refresh_data,
#     trigger="interval",
#     seconds=10
# )


scheduler.start()

@app.get("/")
def root():
    return {"message": "API działa"}
