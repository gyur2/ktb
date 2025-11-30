import io
import json
import sqlite3
from contextlib import contextmanager
from typing import Dict, List

import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms

MODEL_PATH = "fruit_veg_resnet18.pt"
LABEL_PATH = "class_indices.json"
DB_PATH = "predictions.db"

#DB 초기화
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            top1_label TEXT,
            top1_score REAL,
            full_probs TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

#클래스
try:
    with open(LABEL_PATH, "r", encoding="utf-8") as f:
        class_names: List[str] = json.load(f)
except Exception as e:
    print("[FATAL] 라벨 로딩 실패:", e)
    class_names = []

#모델
def build_model(num_classes):
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model

try:
    model = build_model(len(class_names))
    state = torch.load(MODEL_PATH, map_location="cpu")
    model.load_state_dict(state)
    model.eval()
except Exception as e:
    print("[FATAL] 모델 로딩 실패:", e)
    model = None

preprocess_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])


def preprocess_image(image_bytes: bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="업로드된 파일을 이미지로 열 수 없습니다.")

    image = preprocess_tf(image)
    return image.unsqueeze(0)

class PredictionResponse(BaseModel):
    id: int
    top1_label: str
    top1_score: float
    probabilities: Dict[str, float]


class PredictionRecord(BaseModel):
    id: int
    filename: str
    top1_label: str
    top1_score: float
    probabilities: Dict[str, float]
    created_at: str


app = FastAPI(title="과일·야채 분류 + DB 저장 API")


@app.on_event("startup")
def startup():
    init_db()

@app.post("/predict-fruit-veg", response_model=PredictionResponse)
async def predict_fruit_veg(file: UploadFile = File(...)):
    if model is None or not class_names:
        raise HTTPException(status_code=500, detail="모델 또는 라벨 로딩 실패")

    if file.content_type not in {"image/jpeg", "image/jpg", "image/png"}:
        raise HTTPException(status_code=415, detail="JPEG/PNG만 허용됩니다")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="비어있는 파일")

    img_tensor = preprocess_image(image_bytes)

    with torch.no_grad():
        preds = model(img_tensor)
        probs = torch.softmax(preds, dim=1)[0].numpy()

    top_idx = int(np.argmax(probs))
    proba_dict = {class_names[i]: float(probs[i]) for i in range(len(class_names))}
    #DB 저장
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO predictions (filename, top1_label, top1_score, full_probs)
            VALUES (?, ?, ?, ?)
            """,
            (file.filename, class_names[top_idx], float(probs[top_idx]), json.dumps(proba_dict))
        )
        conn.commit()
        pred_id = cur.lastrowid

    return PredictionResponse(
        id=pred_id,
        top1_label=class_names[top_idx],
        top1_score=float(probs[top_idx]),
        probabilities=proba_dict,
    )


@app.get("/predictions", response_model=List[PredictionRecord])
async def list_predictions():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, filename, top1_label, top1_score, full_probs, created_at FROM predictions")
        rows = cur.fetchall()

    results = []
    for row in rows:
        pid, filename, top1_label, top1_score, full_probs, created_at = row
        results.append(
            PredictionRecord(
                id=pid,
                filename=filename,
                top1_label=top1_label,
                top1_score=top1_score,
                probabilities=json.loads(full_probs),
                created_at=created_at
            )
        )
    return results

@app.get("/predictions/{pid}", response_model=PredictionRecord)
async def get_prediction(pid: int):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, filename, top1_label, top1_score, full_probs, created_at FROM predictions WHERE id = ?",
            (pid,)
        )
        row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="해당 ID의 예측 기록 없음")

    pid, filename, top1_label, top1_score, full_probs, created_at = row

    return PredictionRecord(
        id=pid,
        filename=filename,
        top1_label=top1_label,
        top1_score=top1_score,
        probabilities=json.loads(full_probs),
        created_at=created_at
    )
