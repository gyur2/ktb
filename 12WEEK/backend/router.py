# router.py
import io
import json
import numpy as np
import os
from typing import Optional, List, Dict
import uuid
from pathlib import Path

from fastapi import APIRouter, Query, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth import get_current_user

from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms

from db import get_db
from models import User
from controllers import (
    SignupRequest,
    LoginRequest,
    CreatePostRequest,
    UpdatePostRequest,
    CreateCommentRequest,
    UpdateCommentRequest,
    UpdateProfileRequest,
    UpdatePasswordRequest,
    signup_controller,
    login_controller,
    get_profile_controller,
    update_profile_controller,
    update_password_controller,
    create_post_controller,
    list_posts_controller,
    post_detail_controller,
    update_post_controller,
    delete_post_controller,
    create_comment_controller,
    update_comment_controller,
    ToggleLikeRequest,
    toggle_like_controller
)

# ----- 경로 설정 -----
BASE_DIR = Path(__file__).resolve().parent        # backend/
MEDIA_DIR = BASE_DIR / "media"
UPLOAD_DIR = MEDIA_DIR / "post_images"            # 게시글용 이미지 폴더
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
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
router = APIRouter()


# ========== 유저 ==========
@router.post("/users/signup")
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    nickname: str = Form(...),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    # 이메일/닉네임 중복 체크
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
      raise HTTPException(status_code=400, detail="이메일이 중복되었습니다")

    existing_nick = db.query(User).filter(User.nickname == nickname).first()
    if existing_nick:
      raise HTTPException(status_code=400, detail="닉네임이 중복되었습니다")

    # 프로필 이미지 저장
    file_path = None
    if profile_image:
        save_dir = "media/profile"
        os.makedirs(save_dir, exist_ok=True)
        file_path = f"{save_dir}/{profile_image.filename}"
        with open(file_path, "wb") as f:
            f.write(await profile_image.read())

    user = User(
        email=email,
        password=password,   # 실제 서비스면 해시해야 함
        nickname=nickname,
        profile_image=file_path,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "register_success", "data": {"user_id": user.user_id}}


@router.post("/users/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    return login_controller(db, body)


@router.get("/users/me")
def get_profile(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_profile_controller(db, current_user.user_id)



@router.patch("/users/me")
def update_profile(
    body: UpdateProfileRequest,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    return update_profile_controller(db, body, user_id=user_id)


@router.patch("/users/me/password")
def update_password(
    body: UpdatePasswordRequest,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    return update_password_controller(db, body, user_id=user_id)


# ========== 게시글 ==========

@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="no_file")

    ext = Path(file.filename).suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename

    # 실제 파일 저장
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # 브라우저에서 바로 쓸 URL (main.py에서 /media 가 media/ 로 mount 됨)
    url = f"/media/post_images/{filename}"
    return {"url": url}


    
@router.post("/posts")
def create_post(
    body: CreatePostRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return create_post_controller(db, body, user_id=current_user.user_id)


@router.get("/posts")
def list_posts(
    cursor: Optional[int] = Query(default=None),
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return list_posts_controller(db, cursor, limit)


@router.get("/posts/{post_id}")
def post_detail(post_id: int, db: Session = Depends(get_db)):
    return post_detail_controller(db, post_id)


@router.patch("/posts/{post_id}")
def update_post(
    post_id: int,
    body: UpdatePostRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return update_post_controller(db, post_id, body, user_id=current_user.user_id)


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return delete_post_controller(db, post_id, user_id=current_user.user_id)

@router.post("/posts/{post_id}/like")
def toggle_like(
    post_id: int,
    body: ToggleLikeRequest,
    db: Session = Depends(get_db),
    #current_user = Depends(get_current_user),
):
    return toggle_like_controller(db, post_id, body.is_like)

# ========== 댓글 ==========

@router.post("/posts/{post_id}/comments")
def create_comment(
    post_id: int,
    body: CreateCommentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return create_comment_controller(db, post_id, body, user_id=current_user.user_id)



@router.patch("/posts/{post_id}/comments/{comment_id}")
def update_comment(
    post_id: int,
    comment_id: int,
    body: UpdateCommentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return update_comment_controller(
        db,              
        post_id,
        comment_id,
        body,
        user_id=current_user.user_id
    )

# ========== 홈 화면용 이미지 업로드 ==========

@router.post("/predict-fruit-veg")
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