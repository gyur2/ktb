# main.py
from fastapi import FastAPI
from routers.router import router

app = FastAPI(title="Community API - Route + Controller")

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "community api alive"}
