# FastAPI 실습

FastAPI를 사용해 구현한 간단한 커뮤니티 백엔드입니다.  
Route - Controller - Model 패턴을 적용했고, DB 대신 파이썬 `dict`를 이용한 더미 데이터로 동작합니다.

과제 요구사항:
- Route만 사용 → Route + Controller 분리 → Route - Controller - Model 패턴 적용
- DB 미사용, JSON 기반 더미 데이터 사용 (`users = {}`, `posts = {}`, `comments = {}`)
- Postman / Swagger를 통한 요청 시 예외 처리
---

## 🛠 Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn (개발 서버)

---

## 📁 폴더 구조

```text
9week_4/
├── main.py
├── users_dict.py            # 유저 더미 데이터 (20명)
├── posts_dict.py            # 게시글 더미 데이터 (50개)
├── comments_dict.py         # 댓글 더미 데이터 (50개 - 게시글마다 랜덤)
│
├── models/
│   └── models.py            # Model 계층: dict 읽기/쓰기 로직
│
├── controllers/
│   └── controllers.py       # Controller 계층: 비즈니스 로직, 예외 처리
│
└── routers/
    └── router.py            # Route 계층: URL → Controller 연결 (FastAPI 엔드포인트 정의)
