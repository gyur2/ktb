# main.py
from fastapi import FastAPI
from routers.router import router

app = FastAPI(title="9주차 과제 4번")

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Hello ktb~"}
