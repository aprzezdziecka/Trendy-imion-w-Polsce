from fastapi import FastAPI
from database import engine
from models import Base

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API działa"}


@app.get("/health")
def health():
    return {"status": "ok"}


Base.metadata.create_all(bind=engine)