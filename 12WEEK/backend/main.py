from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db import engine, Base
from router import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="과즙상 모임 커뮤니티 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory="media"), name="media")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(router)
