# 🍎 FastAPI 과일·야채 이미지 분류 모델 서빙 API  
11주차 과제 – FastAPI 기반 AI 모델 서빙(10주차 과제) + 예측 결과 DB 저장

---

## 📘 프로젝트 개요
PyTorch로 학습한 과일·야채 이미지 분류 모델(ResNet18)을  
FastAPI 서버로 배포하고, 업로드된 이미지를 기반으로 예측한 결과를  
SQLite DB에 기록하도록 구현한 프로젝트입니다.

또한 모든 요청에 대해 예외처리를 철저히 구현하여  
Postman을 통한 다양한 비정상 입력에도 안정적으로 응답하도록 구성했습니다.

---

## 🧠 주요 기능

### ✅ 1. 이미지 분류 API
POST `/predict-fruit-veg`  
- 업로드된 이미지를 PyTorch 모델로 예측  
- 최고 확률(top-1) 결과 반환  
- 전체 클래스 확률 반환  
- 예측 결과를 SQLite DB에 저장

### ✅ 2. 예측 기록 조회 API
GET `/predictions`  
- DB에 저장된 모든 예측 기록 조회  
- 이미지명, 예측 결과, 스코어, 요청 시간 포함

### ✅ 3. 예외처리(중요 – 과제 필수 조건)
모든 요청에서 다양한 오류를 처리하도록 구현

- 파일이 없을 때 → 422 자동 처리 (FastAPI Validation)
- Content-Type 오류 → 415 반환
- 이미지 파싱 실패 → 400 반환
- 모델 로드 실패 → 500 반환
- DB 오류 처리 → 500 반환

---

## 🗂 디렉토리 구조
```text
11week/
│
├── be_main.py # FastAPI 서버 (모델 + DB + API)
├── fe_main.py # Streamlit 프론트엔드
├── model.py # 모델 학습 코드
│
├── fruit_veg_resnet18.pt # 학습된 모델 가중치
├── class_indices.json # 클래스 라벨링 파일
│
├── db.py # SQLite DB 설정 및 CRUD
├── schemas.py # Pydantic 스키마 정의
│
└── README.md
```
---

## 🚀 실행 방법
### 백엔드 서버 실행
`uvicorn be_main:app --reload`
### 프론트 실행
`streamlit run fe_main.py`


