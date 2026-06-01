from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import gus, names

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(names.router)
app.include_router(gus.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "API działa"}
