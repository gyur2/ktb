import io
import json
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
IMG_SIZE = (224, 224)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
}

try:
    with open(LABEL_PATH, "r", encoding="utf-8") as f:
        class_names: List[str] = json.load(f)
except Exception as e:
    print(f"[FATAL] 클래스 라벨 로딩 실패: {e}")
    class_names = []

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
    print(f"[FATAL] 모델 로딩 실패: {e}")
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="업로드된 파일을 이미지로 열 수 없습니다.",
        )

    image = preprocess_tf(image)
    return image.unsqueeze(0)  # shape: (1, 3, 224, 224)


class PredictionResponse(BaseModel):
    top1_label: str
    top1_score: float
    probabilities: Dict[str, float]


app = FastAPI(title="과일, 야채 분류 PyTorch 모델 API")

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
}


@app.post("/predict-fruit-veg", response_model=PredictionResponse)
async def predict_fruit_veg(file: UploadFile = File(...)):
    if model is None or not class_names:
        raise HTTPException(
            status_code=500,
            detail="모델 또는 클래스 정보가 로딩되지 않았습니다."
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="이미지 파일(JPEG/PNG)만 업로드 가능합니다."
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="비어있는 파일입니다."
        )

    img_tensor = preprocess_image(image_bytes)

    with torch.no_grad():
        preds = model(img_tensor)
        probs = torch.softmax(preds, dim=1)[0].numpy()

    top_idx = int(np.argmax(probs))

    proba_dict = {
        class_names[i]: float(probs[i]) for i in range(len(class_names))
    }

    return PredictionResponse(
        top1_label=class_names[top_idx],
        top1_score=float(probs[top_idx]),
        probabilities=proba_dict,
    )
