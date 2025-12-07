import os
import io
import json
from typing import Dict, List

import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms

# ----- 경로 설정 -----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "fruit_veg_resnet18.pt")
LABEL_PATH = os.path.join(BASE_DIR, "class_indices.json")

# ----- 라벨 / 모델 로딩 -----
try:
    with open(LABEL_PATH, "r", encoding="utf-8") as f:
        class_names: List[str] = json.load(f)
except Exception as e:
    print("[FATAL] 라벨 로딩 실패:", e)
    class_names = []

def build_model(num_classes: int):
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
    top1_label: str
    top1_score: float
    probabilities: Dict[str, float]


app = FastAPI(title="Fruit/Veg Demo (Backend)")


# (사실 같은 origin이라 CORS 없어도 되지만, 있어도 상관 없음)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- 프론트: index.html 파일을 읽어서 반환 -----
@app.get("/", response_class=HTMLResponse)
async def root_page():
    html_path = os.path.join(BASE_DIR, "index.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>index.html 파일을 찾을 수 없습니다.</h1>",
            status_code=500,
        )


# ----- 백엔드: 예측 엔드포인트 -----
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

    return PredictionResponse(
        top1_label=class_names[top_idx],
        top1_score=float(probs[top_idx]),
        probabilities=proba_dict,
    )
